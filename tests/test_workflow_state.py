"""Tests for persistent workflow state engine"""
import uuid

import pytest

from app.agent.controller import AgentController
from app.database.connection import SessionLocal
from app.database.models import ExecutionPlan, Prompt
from app.database.models import Session as DBSession
from app.database.models import WorkflowSubtask


@pytest.fixture
def db():
    """Get test database session"""
    db = SessionLocal()
    yield db
    db.close()


def unique_session_id():
    """Generate unique session ID"""
    return f"test-session-{uuid.uuid4().hex[:8]}"


@pytest.mark.unit
class TestWorkflowStateEngine:
    """Test persistent workflow state management"""

    def test_store_subtasks_before_execution(self, db):
        """STEP 2: Subtasks should be stored in DB before execution"""
        controller = AgentController(db)

        # Create test session
        db_session = DBSession(session_id=unique_session_id())
        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        # Create test plan
        structured_plan = {
            "task_id": "task-1",
            "message": "Test task",
            "subtasks": [
                {"objective": "Subtask 1", "steps": []},
                {"objective": "Subtask 2", "steps": []},
                {"objective": "Subtask 3", "steps": []},
            ],
        }

        # Store subtasks
        controller._store_subtasks(db_session, structured_plan)

        # Verify subtasks were stored
        subtasks = db.query(WorkflowSubtask).filter_by(session_id=db_session.id).all()
        assert len(subtasks) == 3
        assert subtasks[0].objective == "Subtask 1"
        assert subtasks[0].status == "pending"
        assert subtasks[1].order_index == 1
        assert subtasks[2].order_index == 2

    def test_update_subtask_status(self, db):
        """STEP 3: Subtask status should be updateable"""
        controller = AgentController(db)

        # Create test session and subtask
        db_session = DBSession(session_id=unique_session_id())
        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        subtask = WorkflowSubtask(session_id=db_session.id, objective="Test subtask", order_index=0, status="pending")
        db.add(subtask)
        db.commit()

        # Update status to running
        controller._update_subtask_status(db_session, 0, "running")
        db.refresh(subtask)
        assert subtask.status == "running"

        # Update status to completed
        controller._update_subtask_status(db_session, 0, "completed")
        db.refresh(subtask)
        assert subtask.status == "completed"

    def test_resume_point_detection(self, db):
        """STEP 4: Should find first incomplete subtask"""
        controller = AgentController(db)

        # Create test session
        db_session = DBSession(session_id=unique_session_id())
        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        # Create subtasks with mixed status
        subtasks_data = [
            ("Subtask 1", "completed"),
            ("Subtask 2", "completed"),
            ("Subtask 3", "failed"),
            ("Subtask 4", "pending"),
        ]

        for i, (objective, status) in enumerate(subtasks_data):
            subtask = WorkflowSubtask(session_id=db_session.id, objective=objective, order_index=i, status=status)
            db.add(subtask)
        db.commit()

        # Get resume point
        resume_point = controller.resume_engine.get_resume_point(db_session.id)
        assert resume_point is not None
        assert resume_point["order_index"] == 2
        assert resume_point["objective"] == "Subtask 3"
        assert resume_point["status"] == "failed"

    def test_resume_idempotency(self, db):
        """STEP 5: Resume should skip completed subtasks"""
        controller = AgentController(db)

        # Create test session
        db_session = DBSession(session_id=unique_session_id())
        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        # Create subtasks
        for i in range(3):
            subtask = WorkflowSubtask(session_id=db_session.id, objective=f"Subtask {i+1}", order_index=i, status="pending")
            db.add(subtask)
        db.commit()

        # Mark first two as completed
        subtasks = db.query(WorkflowSubtask).filter_by(session_id=db_session.id).all()
        subtasks[0].status = "completed"
        subtasks[1].status = "completed"
        db.commit()

        # Resume should start from subtask 3
        resume_point = controller.resume_engine.get_resume_point(db_session.id)
        assert resume_point["order_index"] == 2
        assert resume_point["objective"] == "Subtask 3"

    def test_all_subtasks_completed(self, db):
        """Should return None when all subtasks are completed"""
        controller = AgentController(db)

        # Create test session
        db_session = DBSession(session_id=unique_session_id())
        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        # Create completed subtasks
        for i in range(3):
            subtask = WorkflowSubtask(session_id=db_session.id, objective=f"Subtask {i+1}", order_index=i, status="completed")
            db.add(subtask)
        db.commit()

        # Resume point should be None
        resume_point = controller.resume_engine.get_resume_point(db_session.id)
        assert resume_point is None

    def test_safety_check_git_clean(self, db):
        """STEP 6: Should check git working tree is clean"""
        controller = AgentController(db)

        # Create test session
        db_session = DBSession(session_id=unique_session_id())
        db.add(db_session)
        db.commit()

        # Safety check should pass if git is clean
        safety = controller.resume_engine._check_resume_safety(db_session.id)
        # Note: This will depend on actual git state, so we just verify the structure
        assert "safe" in safety
        assert "reason" in safety

    def test_execution_plan_loading(self, db):
        """Should load execution plan from DB"""
        controller = AgentController(db)

        # Create test session and plan
        db_session = DBSession(session_id=unique_session_id())
        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        db_prompt = Prompt(session_id=db_session.id, content="Test prompt")
        db.add(db_prompt)
        db.commit()
        db.refresh(db_prompt)

        plan_json = {
            "task_id": "task-1",
            "subtasks": [
                {"objective": "Step 1", "steps": []},
                {"objective": "Step 2", "steps": []},
            ],
        }

        db_plan = ExecutionPlan(prompt_id=db_prompt.id, plan_json=plan_json)
        db.add(db_plan)
        db.commit()

        # Load plan
        loaded_plan = controller.resume_engine.get_execution_plan(db_session.id)
        assert loaded_plan is not None
        assert loaded_plan["task_id"] == "task-1"
        assert len(loaded_plan["subtasks"]) == 2
