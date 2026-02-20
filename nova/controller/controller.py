import logging
import os
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from nova.config.settings import settings
from nova.controller.dispatcher import ToolDispatcher
from nova.controller.parser import PlanParser
from nova.controller.planner import Planner
from nova.controller.retry_engine import RetryEngine
from nova.database.models import ExecutionPlan, ExecutionResult, ExecutionStep, Prompt
from nova.database.models import Session as DBSession
from nova.database.models import WorkflowStep, WorkflowSubtask
from nova.observability.metrics_tracker import MetricsTracker
from nova.policy.engine import PolicyEngine
from nova.recovery.resume_engine import ResumeEngine
from nova.security.command_validator import CommandSecurityError, CommandValidator

logger = logging.getLogger(__name__)


class AgentController:
    def __init__(self, db: Session, simulate: bool = False, plan_only: bool = False):
        self.db = db
        self.simulate = simulate
        self.plan_only = plan_only
        self.planner = Planner(db)  # ✅ Context-aware planner
        self.parser = PlanParser()
        self.dispatcher = ToolDispatcher(use_sandbox=settings.USE_SANDBOX)
        self.retry_engine = RetryEngine(db, self.dispatcher)  # ✅ Required for failure handling
        self.policy_engine = PolicyEngine()
        self.resume_engine = ResumeEngine(db)  # ✅ Resume capability

    def _store_subtasks(self, db_session: DBSession, structured_plan: dict):
        """Store all subtasks in DB before execution (STEP 2)"""
        for index, subtask in enumerate(structured_plan.get("subtasks", [])):
            db_subtask = WorkflowSubtask(
                session_id=db_session.id, objective=subtask.get("objective", ""), order_index=index, status="pending"
            )
            self.db.add(db_subtask)
        self.db.commit()

    def _update_subtask_status(self, db_session: DBSession, subtask_index: int, status: str):
        """Update subtask status in DB (STEP 3)"""
        subtask = self.db.query(WorkflowSubtask).filter_by(session_id=db_session.id, order_index=subtask_index).first()
        if subtask:
            subtask.status = status  # type: ignore
            self.db.commit()

    def resume(self, session_id: int):
        """Resume a failed workflow from the last incomplete subtask (STEP 4)"""
        logger.info(f"Resuming session {session_id}")

        # STEP 6: Safety checks
        safety_check = self.resume_engine._check_resume_safety(session_id)
        if not safety_check["safe"]:
            logger.warning(f"Resume blocked for session {session_id}: {safety_check['reason']}")
            return {"error": f"Resume blocked: {safety_check['reason']}"}

        # Get resume point
        resume_point = self.resume_engine.get_resume_point(session_id)
        if not resume_point:
            logger.info(f"All subtasks already completed for session {session_id}")
            return {"message": "All subtasks already completed"}

        # Load execution plan
        structured_plan = self.resume_engine.get_execution_plan(session_id)
        if not structured_plan:
            logger.error(f"Execution plan not found for session {session_id}")
            return {"error": "Execution plan not found"}

        # Load session
        db_session = self.db.query(DBSession).filter_by(id=session_id).first()
        if not db_session:
            logger.error(f"Session {session_id} not found")
            return {"error": f"Session {session_id} not found"}

        # Initialize metrics
        metrics = MetricsTracker(session_id=int(db_session.id), max_operations=4)

        logger.info(f"Resuming from: {resume_point['objective']}")
        print(f"🔄 Resuming from: {resume_point['objective']}")
        print(f"   Status: {resume_point['status']}")

        # Execute from resume point onwards (STEP 5: Idempotent)
        subtasks = self.db.query(WorkflowSubtask).filter_by(session_id=session_id).order_by(WorkflowSubtask.order_index).all()

        for subtask_index in range(resume_point["order_index"], len(subtasks)):
            subtask_obj = subtasks[subtask_index]

            # Skip if already completed (idempotent)
            if subtask_obj.status == "completed":
                logger.debug(f"Skipping already completed subtask {subtask_index}")
                continue

            # Find corresponding subtask in structured plan
            if subtask_index < len(structured_plan.get("subtasks", [])):
                subtask_plan = structured_plan["subtasks"][subtask_index]

                # Mark as running
                self.resume_engine.mark_subtask_running(int(subtask_obj.id))

                # Execute steps
                subtask_failed = False
                for step in subtask_plan.get("steps", []):
                    # Policy evaluation
                    decision = self.policy_engine.evaluate(step)
                    if not decision.allowed:
                        logger.warning(f"Policy blocked step during resume: {decision.reason}")
                        print(f"❌ Policy blocked step: {decision.reason}")
                        subtask_failed = True
                        break

                    # Security validation
                    try:
                        CommandValidator.validate(step.get("command"))
                    except CommandSecurityError:
                        logger.error("Command security validation failed during resume")
                        subtask_failed = True
                        break

                    # Execute step
                    logger.debug(f"Executing resumed step: {step.get('action')}")
                    result = self.dispatcher.dispatch(step, metrics)
                    if result and result.return_code != 0:
                        logger.error(f"Resumed step failed: {result.stderr}")
                        subtask_failed = True
                        break

                # Update subtask status
                if subtask_failed:
                    logger.warning(f"Subtask {subtask_index} failed during resume")
                    self.resume_engine.mark_subtask_failed(int(subtask_obj.id))
                    break
                else:
                    logger.info(f"Subtask {subtask_index} completed during resume")
                    self.resume_engine.mark_subtask_completed(int(subtask_obj.id))

        # Persist final metrics
        db_session.read_count = metrics.read_count  # type: ignore
        db_session.write_count = metrics.write_count  # type: ignore
        db_session.retry_count = metrics.retry_count  # type: ignore
        db_session.risk_score = metrics.risk_score  # type: ignore
        self.db.commit()

        logger.info(f"Resume completed from subtask {resume_point['order_index']}")
        return {"message": f"Resume completed from subtask {resume_point['order_index']}"}

    def _execute_subtasks(
        self,
        db_session: DBSession,
        db_plan: ExecutionPlan,
        structured_plan: dict,
        metrics: MetricsTracker,
    ):
        """Execute subtasks with state tracking (STEP 3)"""
        for subtask_index, subtask in enumerate(structured_plan.get("subtasks", [])):
            # Mark subtask as running
            self._update_subtask_status(db_session, subtask_index, "running")

            # Get or create subtask record
            db_subtask = self.db.query(WorkflowSubtask).filter_by(session_id=db_session.id, order_index=subtask_index).first()

            subtask_failed = False
            for step_index, step in enumerate(subtask.get("steps", [])):
                # Create WorkflowStep record for tracking
                workflow_step = WorkflowStep(
                    session_id=db_session.id,
                    subtask_id=db_subtask.id if db_subtask else None,
                    step_index=step_index,
                    command=step.get("command"),
                    status="pending",
                )
                self.db.add(workflow_step)
                self.db.commit()
                self.db.refresh(workflow_step)

                db_step = ExecutionStep(
                    plan_id=db_plan.id,
                    step_order=step_index + 1,
                    tool=step.get("tool"),
                    action=step.get("action"),
                    command=step.get("command"),
                    file_path=step.get("file_path"),
                    content=step.get("content"),
                )

                self.db.add(db_step)
                self.db.commit()
                self.db.refresh(db_step)

                # 🔐 Policy evaluation
                decision = self.policy_engine.evaluate(step)
                if not decision.allowed:
                    logger.warning(f"Policy blocked step: {step.get('action')} - {decision.reason}")
                    print(f"❌ Policy blocked step: {decision.reason}")
                    workflow_step.status = "failed"
                    self.db.commit()
                    subtask_failed = True
                    break

                if decision.risk_level == "high":
                    logger.warning(f"High-risk step detected: {step.get('action')} - " f"{decision.reason}")
                    print(f"⚠️  High-risk step detected: {decision.reason}")

                # 🔐 Validate command security
                try:
                    CommandValidator.validate(step.get("command"))
                except CommandSecurityError:
                    logger.error(f"Command security validation failed: {step.get('command')}")
                    workflow_step.status = "failed"
                    self.db.commit()
                    subtask_failed = True
                    break

                # Mark step as running
                workflow_step.status = "running"
                workflow_step.started_at = datetime.utcnow()
                self.db.commit()

                logger.debug(f"Executing step: {step.get('tool')} - {step.get('action')}")
                result = self.dispatcher.dispatch(step, metrics)
                # 🚀 Execute step

                if result:
                    db_result = ExecutionResult(
                        step_id=db_step.id,
                        stdout=result.stdout,
                        stderr=result.stderr,
                        return_code=result.return_code,
                    )

                    self.db.add(db_result)
                    self.db.commit()

                    # Mark step as completed
                    workflow_step.finished_at = datetime.utcnow()
                    workflow_step.status = "completed"
                    self.db.commit()

                    # HIGH RISK CHECK
                    if metrics.should_block():
                        logger.error(
                            f"Operation limit exceeded. Risk score: {metrics.risk_score}, "
                            f"Max operations: {metrics.max_operations}"
                        )
                        print(f"⚠ HIGH RISK: Operation limit exceeded " f"(max {metrics.max_operations})")
                        print(f"Risk Score: {metrics.risk_score}")
                        print("Execution stopped due to risk threshold.")

                        metrics.track_retry()

                        # Save metrics before rerun
                        db_session.read_count = metrics.read_count  # type: ignore
                        db_session.write_count = metrics.write_count  # type: ignore
                        db_session.retry_count = metrics.retry_count  # type: ignore
                        db_session.risk_score = metrics.risk_score  # type: ignore
                        self.db.commit()

                        # Mark subtask as failed
                        self._update_subtask_status(db_session, subtask_index, "failed")
                        return {"status": "blocked"}

                    # Normal failure handling
                    # 🔁 Handle failure if needed
                    if result.return_code != 0:
                        logger.error(f"Step failed with return code {result.return_code}: " f"{result.stderr}")
                        workflow_step.status = "failed"
                        self.db.commit()
                        self.retry_engine.handle_failure(
                            db_step=db_step,
                            original_step=step,
                            error_message=result.stderr,
                            session_id=db_session.session_id,
                        )
                        subtask_failed = True
                        break
                    else:
                        logger.info(f"Step completed successfully: {step.get('action')}")

            # Mark subtask as completed or failed
            if subtask_failed:
                self._update_subtask_status(db_session, subtask_index, "failed")
            else:
                self._update_subtask_status(db_session, subtask_index, "completed")

    def run(self, user_prompt: str):
        from sqlalchemy.exc import ProgrammingError

        logger.info(f"Starting execution with prompt: {user_prompt[:100]}")

        adaptive_limit = 4

        try:
            last_sessions = self.db.query(DBSession).order_by(DBSession.id.desc()).limit(3).all()

            if last_sessions:
                avg_risk = sum((s.risk_score or 0) for s in last_sessions) / len(last_sessions)

                if avg_risk > 8:
                    logger.warning(f"High risk detected in recent sessions (avg: {avg_risk}). Entering strict mode.")
                    print("Suggestion: Your recent sessions show high risk behavior.")
                    print("System entering strict mode.")
                    adaptive_limit = 2
        except ProgrammingError:
            # Database tables not initialized, rollback and use default limit
            self.db.rollback()
            pass

        # Check for empty prompt
        if not user_prompt or not user_prompt.strip():
            logger.warning("Empty prompt provided")
            return {"task_id": str(uuid.uuid4()), "message": "Please provide a task description", "steps": []}

        # 1️⃣ Create new session
        session_uuid = str(uuid.uuid4())

        db_session = DBSession(session_id=session_uuid)
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)

        # Initialize metrics tracker
        metrics = MetricsTracker(session_id=int(db_session.id), max_operations=adaptive_limit)

        # 2️⃣ Save prompt
        db_prompt = Prompt(session_id=db_session.id, content=user_prompt)
        self.db.add(db_prompt)
        self.db.commit()
        self.db.refresh(db_prompt)

        # 2️⃣.5️⃣ Pre-check for git initialization
        if "git" in user_prompt.lower() and "init" in user_prompt.lower():
            if os.path.isdir(".git"):
                # Git is already initialized, return early
                return {"task_id": str(uuid.uuid4()), "message": "Git repository is already initialized", "steps": []}

        # 2️⃣.6️⃣ Pre-check for file creation
        if "create" in user_prompt.lower() and ("file" in user_prompt.lower() or "named" in user_prompt.lower()):
            # Extract filename from prompt (look for patterns like "named xyz.txt" or "file xyz.txt")
            import re

            # Try to match "named <filename>" first
            match = re.search(r"named\s+(\S+)", user_prompt.lower())
            if not match:
                # Try to match "file <filename>"
                match = re.search(r"file\s+(\S+)", user_prompt.lower())

            if match:
                filename = match.group(1)
                if os.path.isfile(filename):
                    return {"task_id": str(uuid.uuid4()), "message": f"File '{filename}' already exists", "steps": []}

        # 2️⃣.7️⃣ Pre-check for file modification (when user says "that code", "that file", "optimize that", etc.)
        if any(word in user_prompt.lower() for word in ["optimize", "modify", "update", "change", "fix", "improve"]):
            if any(word in user_prompt.lower() for word in ["that", "the code", "the file", "it"]):
                # Get the most recently modified file
                # Store this in context for the LLM to use
                # We'll pass it through the prompt
                pass

        # 2️⃣.8️⃣ Pre-check for running non-existent files
        if any(word in user_prompt.lower() for word in ["run", "execute", "compile"]):
            import re

            # Try to extract filename from patterns like "run xyz.java" or "execute xyz.py"
            # Look for file extensions - must be a complete filename
            match = re.search(r"(?:run|execute|compile)\s+(\S+\.\w+)", user_prompt.lower())
            if match:
                filename = match.group(1)
                if not os.path.isfile(filename):
                    return {
                        "task_id": str(uuid.uuid4()),
                        "message": f"File '{filename}' does not exist. Please create it first.",
                        "steps": [],
                    }
            else:
                # If no specific filename is mentioned, check if user is asking to run something that doesn't exist
                # This is a more general check for phrases like "run java file that does not exist"
                if "does not exist" in user_prompt.lower() or "doesn't exist" in user_prompt.lower():
                    return {
                        "task_id": str(uuid.uuid4()),
                        "message": "The file you're trying to run does not exist. Please create it first.",
                        "steps": [],
                    }

        # 2️⃣.9️⃣ Pre-check for dangerous operations
        dangerous_patterns = [
            "delete everything",
            "delete all",
            "deleted everything",
            "rm -rf",
            "remove everything",
            "removed everything",
            "clear everything",
            "cleared everything",
            "wipe",
            "destroy",
            "nuke",
        ]
        if any(pattern in user_prompt.lower() for pattern in dangerous_patterns):
            return {
                "task_id": str(uuid.uuid4()),
                "message": (
                    "❌ Dangerous operation blocked: Cannot delete all files or folders. "
                    "Please specify which files to delete."
                ),
                "steps": [],
            }

        # 3️⃣ Generate plan (WITH CONTEXT)
        # Pass external session ID for context memory
        raw_plan = self.planner.generate_plan(user_prompt, session_uuid)

        # 4️⃣ Validate JSON plan
        structured_plan = self.parser.validate(raw_plan)

        # 5️⃣ Save execution plan
        import json

        db_plan = ExecutionPlan(prompt_id=db_prompt.id, plan_json=json.dumps(structured_plan))
        self.db.add(db_plan)
        self.db.commit()
        self.db.refresh(db_plan)

        # 🧠 STEP 2: Store subtasks before execution
        self._store_subtasks(db_session, structured_plan)

        # 6️⃣ Execute each step (or simulate/plan-only)
        if self.plan_only:
            # In plan-only mode, evaluate risk for each step but don't execute
            # Flatten subtasks into steps
            all_steps = []
            for subtask in structured_plan.get("subtasks", []):
                all_steps.extend(subtask.get("steps", []))

            steps_with_risk = []
            for step in all_steps:
                decision = self.policy_engine.evaluate(step)
                step_with_risk = {
                    **step,
                    "risk": decision.risk_level,
                    "policy_reason": decision.reason,
                    "allowed": decision.allowed,
                }
                steps_with_risk.append(step_with_risk)

            return {
                "task_id": structured_plan.get("task_id"),
                "message": structured_plan.get("message"),
                "steps": steps_with_risk,
                "plan_only": True,
            }

        if self.simulate:
            # In simulation mode, evaluate risk for each step and return with simulation flag
            # Flatten subtasks into steps
            all_steps = []
            for subtask in structured_plan.get("subtasks", []):
                all_steps.extend(subtask.get("steps", []))

            steps_with_risk = []
            for step in all_steps:
                decision = self.policy_engine.evaluate(step)
                step_with_risk = {
                    **step,
                    "risk": decision.risk_level,
                    "policy_reason": decision.reason,
                    "allowed": decision.allowed,
                }
                steps_with_risk.append(step_with_risk)

            return {
                "task_id": structured_plan.get("task_id"),
                "message": structured_plan.get("message"),
                "steps": steps_with_risk,
                "simulation": True,
            }

        # Flatten subtasks into a single steps list
        all_steps = []
        for subtask in structured_plan.get("subtasks", []):
            all_steps.extend(subtask.get("steps", []))

        # 🧠 STEP 3: Execute subtasks with state tracking
        result = self._execute_subtasks(db_session, db_plan, structured_plan, metrics)
        if result and result.get("status") == "blocked":
            return result
        # Persist final metrics
        db_session.read_count = metrics.read_count  # type: ignore
        db_session.write_count = metrics.write_count  # type: ignore
        db_session.retry_count = metrics.retry_count  # type: ignore
        db_session.risk_score = metrics.risk_score  # type: ignore
        self.db.commit()

        # Return the structured plan with flattened steps
        return {
            "task_id": structured_plan.get("task_id"),
            "message": structured_plan.get("message"),
            "steps": all_steps,
            "subtasks": structured_plan.get("subtasks", []),
        }
