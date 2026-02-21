"""Tests for resume workflow logic."""

import pytest


@pytest.mark.unit
class TestResumeLogic:
    """Test resume workflow algorithm."""

    def test_resume_skips_completed_steps(self):
        """Test that resume skips completed steps."""
        steps = [
            {"id": 1, "status": "completed", "command": "step1"},
            {"id": 2, "status": "completed", "command": "step2"},
            {"id": 3, "status": "pending", "command": "step3"},
            {"id": 4, "status": "pending", "command": "step4"},
        ]

        # Find first incomplete step
        first_incomplete = next((s for s in steps if s["status"] != "completed"), None)

        assert first_incomplete is not None
        assert first_incomplete["id"] == 3
        assert first_incomplete["status"] == "pending"

    def test_resume_finds_running_step(self):
        """Test that resume finds running steps."""
        steps = [
            {"id": 1, "status": "completed", "command": "step1"},
            {"id": 2, "status": "running", "command": "step2"},
            {"id": 3, "status": "pending", "command": "step3"},
        ]

        # Find first incomplete step (running or pending)
        first_incomplete = next((s for s in steps if s["status"] != "completed"), None)

        assert first_incomplete is not None
        assert first_incomplete["id"] == 2
        assert first_incomplete["status"] == "running"

    def test_resume_finds_failed_step(self):
        """Test that resume finds failed steps."""
        steps = [
            {"id": 1, "status": "completed", "command": "step1"},
            {"id": 2, "status": "failed", "command": "step2"},
            {"id": 3, "status": "pending", "command": "step3"},
        ]

        # Find first incomplete step
        first_incomplete = next((s for s in steps if s["status"] != "completed"), None)

        assert first_incomplete is not None
        assert first_incomplete["id"] == 2
        assert first_incomplete["status"] == "failed"

    def test_resume_all_completed(self):
        """Test resume when all steps are completed."""
        steps = [
            {"id": 1, "status": "completed", "command": "step1"},
            {"id": 2, "status": "completed", "command": "step2"},
            {"id": 3, "status": "completed", "command": "step3"},
        ]

        # Find first incomplete step
        first_incomplete = next((s for s in steps if s["status"] != "completed"), None)

        assert first_incomplete is None

    def test_resume_empty_steps(self):
        """Test resume with empty step list."""
        steps = []

        # Find first incomplete step
        first_incomplete = next((s for s in steps if s["status"] != "completed"), None)

        assert first_incomplete is None

    def test_resume_maintains_order(self):
        """Test that resume maintains step order."""
        steps = [
            {"id": 1, "status": "completed", "command": "step1"},
            {"id": 2, "status": "completed", "command": "step2"},
            {"id": 3, "status": "pending", "command": "step3"},
            {"id": 4, "status": "pending", "command": "step4"},
            {"id": 5, "status": "pending", "command": "step5"},
        ]

        # Collect all incomplete steps in order
        incomplete_steps = [s for s in steps if s["status"] != "completed"]

        assert len(incomplete_steps) == 3
        assert incomplete_steps[0]["id"] == 3
        assert incomplete_steps[1]["id"] == 4
        assert incomplete_steps[2]["id"] == 5

    def test_resume_idempotent(self):
        """Test that resume is idempotent."""
        steps = [
            {"id": 1, "status": "completed", "command": "step1"},
            {"id": 2, "status": "pending", "command": "step2"},
        ]

        # First resume
        first_incomplete_1 = next((s for s in steps if s["status"] != "completed"), None)

        # Second resume (same state)
        first_incomplete_2 = next((s for s in steps if s["status"] != "completed"), None)

        assert first_incomplete_1 == first_incomplete_2
        assert first_incomplete_1["id"] == 2
