"""Resume engine for persistent workflow state management (STEPS 4-6)"""
import subprocess
from typing import Dict, Optional

from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from app.database.models import ExecutionPlan, Prompt
from app.database.models import Session as DBSession
from app.database.models import WorkflowSubtask


class ResumeEngine:
    """Handles workflow resumption from failed subtasks"""

    def __init__(self, db: Session):
        self.db = db

    def _check_git_safety(self) -> Dict:
        """STEP 6: Check if git working tree is clean before resume"""
        try:
            result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=5)

            if result.returncode != 0:
                return {"safe": False, "reason": "Not a git repository"}

            if result.stdout.strip():
                return {"safe": False, "reason": "Git working tree has uncommitted changes"}

            return {"safe": True, "reason": "Git working tree is clean"}
        except Exception as e:
            return {"safe": False, "reason": f"Git check failed: {str(e)}"}

    def _check_resume_safety(self, session_id: int) -> Dict:
        """STEP 6: Comprehensive safety checks before resume"""
        try:
            # Check git status
            git_check = self._check_git_safety()
            if not git_check["safe"]:
                return {"safe": False, "reason": f"Git safety check failed: {git_check['reason']}"}

            # Check for conflicting state
            db_session = self.db.query(DBSession).filter_by(id=session_id).first()
            if not db_session:
                return {"safe": False, "reason": "Session not found"}

            # Check if any subtask is currently running
            running_subtasks = self.db.query(WorkflowSubtask).filter_by(session_id=session_id, status="running").all()
            if running_subtasks:
                return {"safe": False, "reason": "Session has running subtasks"}

            return {"safe": True, "reason": "All safety checks passed"}
        except ProgrammingError:
            return {"safe": False, "reason": "Database tables not initialized"}

    def get_resume_point(self, session_id: int) -> Optional[Dict]:
        """Find the first incomplete subtask to resume from"""
        try:
            subtasks = (
                self.db.query(WorkflowSubtask).filter_by(session_id=session_id).order_by(WorkflowSubtask.order_index).all()
            )

            for subtask in subtasks:
                if subtask.status != "completed":
                    return {
                        "subtask_id": subtask.id,
                        "order_index": subtask.order_index,
                        "objective": subtask.objective,
                        "status": subtask.status,
                    }

            return None
        except ProgrammingError:
            return None

    def get_execution_plan(self, session_id: int) -> Optional[Dict]:
        """Load the execution plan for a session"""
        import json

        try:
            db_prompt = self.db.query(Prompt).filter_by(session_id=session_id).first()
            if not db_prompt:
                return None

            db_plan = self.db.query(ExecutionPlan).filter_by(prompt_id=db_prompt.id).first()
            if not db_plan:
                return None

            # Deserialize JSON if it's a string
            plan_json = db_plan.plan_json
            if isinstance(plan_json, str):
                return json.loads(plan_json)
            return plan_json
        except ProgrammingError:
            return None

    def mark_subtask_running(self, subtask_id: int):
        """Mark a subtask as running"""
        try:
            subtask = self.db.query(WorkflowSubtask).filter_by(id=subtask_id).first()
            if subtask:
                subtask.status = "running"
                self.db.commit()
        except ProgrammingError:
            pass

    def mark_subtask_completed(self, subtask_id: int):
        """Mark a subtask as completed"""
        try:
            subtask = self.db.query(WorkflowSubtask).filter_by(id=subtask_id).first()
            if subtask:
                subtask.status = "completed"
                self.db.commit()
        except ProgrammingError:
            pass

    def mark_subtask_failed(self, subtask_id: int):
        """Mark a subtask as failed"""
        try:
            subtask = self.db.query(WorkflowSubtask).filter_by(id=subtask_id).first()
            if subtask:
                subtask.status = "failed"
                self.db.commit()
        except ProgrammingError:
            pass
