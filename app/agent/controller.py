import uuid
from sqlalchemy.orm import Session
from app.database.models import Session as DBSession, Prompt, ExecutionPlan
from app.agent.planner import Planner
from app.agent.parser import PlanParser
from app.agent.dispatcher import ToolDispatcher


class AgentController:

    def __init__(self, db: Session):
        self.db = db
        self.planner = Planner()
        self.parser = PlanParser()

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

        # 3️⃣ Call Planner
        raw_plan = self.planner.generate_plan(user_prompt)

        # 4️⃣ Parse plan
        structured_plan = self.parser.validate(raw_plan)

        # 5️⃣ Save execution plan
        db_plan = ExecutionPlan(
            prompt_id=db_prompt.id,
            plan_json=structured_plan
        )
        self.db.add(db_plan)
        self.db.commit()

        return structured_plan
