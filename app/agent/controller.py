import uuid
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



class AgentController:

    def __init__(self, db: Session):
        self.db = db
        self.planner = Planner()
        self.parser = PlanParser()
        self.dispatcher = ToolDispatcher()

    def run(self, user_prompt: str):

        # 1️⃣ Create session
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

            print("DEBUG STEP TOOL:", step["tool"])
            print("DEBUG STEP COMMAND:", step["command"])


            result = self.dispatcher.dispatch(step)
            print("DEBUG RESULT : ", result)

            if result:
                db_result = ExecutionResult(
                    step_id=db_step.id,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    return_code=result.return_code
                )

                self.db.add(db_result)
                self.db.commit()

                print("\nSTDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                print("RETURN CODE:", result.return_code)

                if result.return_code != 0:
                    self.retry_engine.handle_failure(
                        db_step=db_step,
                        original_step=step,
                        error_message=result.stderr
                    )
