import uuid
from app.observability.metrics_tracker import MetricsTracker
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




class AgentController:

    def __init__(self, db: Session):
        self.db = db
        self.planner = Planner()
        self.parser = PlanParser()
        self.dispatcher = ToolDispatcher(
            use_sandbox=settings.USE_SANDBOX
        )

    def run(self, user_prompt: str):

        last_sessions = (
            self.db.query(DBSession)
            .order_by(DBSession.id.desc())
            .limit(3)
            .all()
        )

        if last_sessions:
            avg_risk = sum((s.risk_score or 0) for s in last_sessions) / len(last_sessions)

            if avg_risk > 8:
                print("Suggestion: Your recent sessions show high risk behavior.")
                print("Consider breaking your prompt into smaller steps.")


        # 1️⃣ Create session
        session_uuid = str(uuid.uuid4())
        db_session = DBSession(session_id=session_uuid)
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)

        # Initialize metrics tracker
        metrics = MetricsTracker(session_id=db_session.id)

        # 2️⃣ Save prompt
        db_prompt = Prompt(
            session_id=db_session.id,
            content=user_prompt
        )
        self.db.add(db_prompt)
        self.db.commit()
        self.db.refresh(db_prompt)

        # 3️⃣ Generate plan
        raw_plan = self.planner.generate_plan(user_prompt)

        # 4️⃣ Validate plan
        structured_plan = self.parser.validate(raw_plan)

        # 5️⃣ Save execution plan
        db_plan = ExecutionPlan(
            prompt_id=db_prompt.id,
            plan_json=structured_plan
        )
        self.db.add(db_plan)
        self.db.commit()
        self.db.refresh(db_plan)

        # 6️⃣ Execute steps
        for index, step in enumerate(structured_plan["steps"]):

            db_step = ExecutionStep(
                plan_id=db_plan.id,
                step_order=index + 1,
                tool=step["tool"],
                action=step["action"],
                command=step["command"],
                file_path=step["file_path"],
                content=step["content"]
            )

            self.db.add(db_step)
            self.db.commit()
            self.db.refresh(db_step)

            try:
                CommandValidator.validate(step["command"])
            except CommandSecurityError as e:
                continue

            result = self.dispatcher.dispatch(step,metrics)

            if result:
                db_result = ExecutionResult(
                    step_id=db_step.id,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    return_code=result.return_code
                )

                self.db.add(db_result)
                self.db.commit()

                
                # HIGH RISK CHECK
                if metrics.should_block():
                    print("⚠ HIGH RISK: Operation limit exceeded (max 4)")
                    print(f"Risk Score: {metrics.risk_score}")
                    print("Execution stopped due to risk threshold.")

                    metrics.track_retry()

                    # Save metrics before rerun
                    db_session.read_count = metrics.read_count
                    db_session.write_count = metrics.write_count
                    db_session.retry_count = metrics.retry_count
                    db_session.risk_score = metrics.risk_score
                    self.db.commit()

                    return


                # Normal failure handling
                if result.return_code != 0:
                    self.retry_engine.handle_failure(
                        db_step=db_step,
                        original_step=step,
                        error_message=result.stderr
                    )
        # Persist final metrics
        db_session.read_count = metrics.read_count
        db_session.write_count = metrics.write_count
        db_session.retry_count = metrics.retry_count
        db_session.risk_score = metrics.risk_score
        self.db.commit()
