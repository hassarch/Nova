import uuid
import os
from sqlalchemy.orm import Session

from app.database.models import (
    Session as DBSession,
    Prompt,
    ExecutionPlan,
    ExecutionStep,
    ExecutionResult
)

from app.agent.planner import Planner
from app.agent.parser import PlanParser
from app.agent.dispatcher import ToolDispatcher
from app.agent.retry_engine import RetryEngine
from app.security.command_validator import CommandValidator, CommandSecurityError
from app.config.settings import settings
from app.core.policy.engine import PolicyEngine



class AgentController:

    def __init__(self, db: Session, simulate: bool = False, plan_only: bool = False):
        self.db = db
        self.simulate = simulate
        self.plan_only = plan_only
        self.planner = Planner(db)  # ✅ Context-aware planner
        self.parser = PlanParser()
        self.dispatcher = ToolDispatcher(
            use_sandbox=settings.USE_SANDBOX
        )
        self.retry_engine = RetryEngine(db,self.dispatcher)  # ✅ Required for failure handling
        self.policy_engine= PolicyEngine()


    def run(self, user_prompt: str):

        # Check for empty prompt
        if not user_prompt or not user_prompt.strip():
            return {
                "task_id": str(uuid.uuid4()),
                "message": "Please provide a task description",
                "steps": []
            }

        # 1️⃣ Create new session
        session_uuid = str(uuid.uuid4())

        db_session = DBSession(session_id=session_uuid)
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)

        # 2️⃣ Save prompt
        db_prompt = Prompt(
            session_id=db_session.id,
            content=user_prompt
        )
        self.db.add(db_prompt)
        self.db.commit()
        self.db.refresh(db_prompt)

        # 2️⃣.5️⃣ Pre-check for git initialization
        if "git" in user_prompt.lower() and "init" in user_prompt.lower():
            if os.path.isdir(".git"):
                # Git is already initialized, return early
                return {
                    "task_id": str(uuid.uuid4()),
                    "message": "Git repository is already initialized",
                    "steps": []
                }

        # 2️⃣.6️⃣ Pre-check for file creation
        if "create" in user_prompt.lower() and ("file" in user_prompt.lower() or "named" in user_prompt.lower()):
            # Extract filename from prompt (look for patterns like "named xyz.txt" or "file xyz.txt")
            import re
            # Try to match "named <filename>" first
            match = re.search(r'named\s+(\S+)', user_prompt.lower())
            if not match:
                # Try to match "file <filename>"
                match = re.search(r'file\s+(\S+)', user_prompt.lower())
            
            if match:
                filename = match.group(1)
                if os.path.isfile(filename):
                    return {
                        "task_id": str(uuid.uuid4()),
                        "message": f"File '{filename}' already exists",
                        "steps": []
                    }

        # 2️⃣.7️⃣ Pre-check for file modification (when user says "that code", "that file", "optimize that", etc.)
        if any(word in user_prompt.lower() for word in ["optimize", "modify", "update", "change", "fix", "improve"]):
            if any(word in user_prompt.lower() for word in ["that", "the code", "the file", "it"]):
                # Get the most recently modified file
                import glob
                files = [f for f in glob.glob("*") if os.path.isfile(f)]
                if files:
                    most_recent = max(files, key=lambda f: os.path.getmtime(f))
                    # Store this in context for the LLM to use
                    # We'll pass it through the prompt
                    pass

        # 2️⃣.8️⃣ Pre-check for running non-existent files
        if any(word in user_prompt.lower() for word in ["run", "execute", "compile"]):
            import re
            # Try to extract filename from patterns like "run xyz.java" or "execute xyz.py"
            # Look for file extensions - must be a complete filename
            match = re.search(r'(?:run|execute|compile)\s+(\S+\.\w+)', user_prompt.lower())
            if match:
                filename = match.group(1)
                if not os.path.isfile(filename):
                    return {
                        "task_id": str(uuid.uuid4()),
                        "message": f"File '{filename}' does not exist. Please create it first.",
                        "steps": []
                    }
            else:
                # If no specific filename is mentioned, check if user is asking to run something that doesn't exist
                # This is a more general check for phrases like "run java file that does not exist"
                if "does not exist" in user_prompt.lower() or "doesn't exist" in user_prompt.lower():
                    return {
                        "task_id": str(uuid.uuid4()),
                        "message": "The file you're trying to run does not exist. Please create it first.",
                        "steps": []
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
            "nuke"
        ]
        if any(pattern in user_prompt.lower() for pattern in dangerous_patterns):
            return {
                "task_id": str(uuid.uuid4()),
                "message": "❌ Dangerous operation blocked: Cannot delete all files or folders. Please specify which files to delete.",
                "steps": []
            }

        # 3️⃣ Generate plan (WITH CONTEXT)
        raw_plan = self.planner.generate_plan(
            user_prompt,
            session_uuid  # Pass external session ID for context memory
        )

        # 4️⃣ Validate JSON plan
        structured_plan = self.parser.validate(raw_plan)

        # 5️⃣ Save execution plan
        db_plan = ExecutionPlan(
            prompt_id=db_prompt.id,
            plan_json=structured_plan
        )
        self.db.add(db_plan)
        self.db.commit()
        self.db.refresh(db_plan)

        # 6️⃣ Execute each step (or simulate/plan-only)
        if self.plan_only:
            # In plan-only mode, return the plan without policy evaluation
            return {
                "task_id": structured_plan.get("task_id"),
                "message": structured_plan.get("message"),
                "steps": structured_plan.get("steps", []),
                "plan_only": True
            }

        if self.simulate:
            # In simulation mode, evaluate risk for each step and return with simulation flag
            steps_with_risk = []
            for step in structured_plan.get("steps", []):
                decision = self.policy_engine.evaluate(step)
                step_with_risk = {
                    **step,
                    "risk": decision.risk_level,
                    "policy_reason": decision.reason,
                    "allowed": decision.allowed
                }
                steps_with_risk.append(step_with_risk)
            
            return {
                "task_id": structured_plan.get("task_id"),
                "message": structured_plan.get("message"),
                "steps": steps_with_risk,
                "simulation": True
            }

        for index, step in enumerate(structured_plan.get("steps", [])):

            db_step = ExecutionStep(
                plan_id=db_plan.id,
                step_order=index + 1,
                tool=step.get("tool"),
                action=step.get("action"),
                command=step.get("command"),
                file_path=step.get("file_path"),
                content=step.get("content")
            )

            self.db.add(db_step)
            self.db.commit()
            self.db.refresh(db_step)

            # 🔐 Policy evaluation
            decision = self.policy_engine.evaluate(step)
            if not decision.allowed:
                print(f"❌ Policy blocked step: {decision.reason}")
                continue

            if decision.risk_level == "high":
                print(f"⚠️  High-risk step detected: {decision.reason}")

            # 🔐 Validate command security
            try:
                CommandValidator.validate(step.get("command"))
            except CommandSecurityError as e:
                # Skip unsafe command
                continue

            # 🚀 Execute step
            result = self.dispatcher.dispatch(step)

            if result:
                db_result = ExecutionResult(
                    step_id=db_step.id,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    return_code=result.return_code
                )

                self.db.add(db_result)
                self.db.commit()

                # 🔁 Handle failure if needed
                if result.return_code != 0:
                    self.retry_engine.handle_failure(
                        db_step=db_step,
                        original_step=step,
                        error_message=result.stderr,
                        session_id=session_uuid  # Required for context-aware retry
                    )

        # Return the structured plan
        return structured_plan
