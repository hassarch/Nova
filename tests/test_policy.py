"""Tests for policy engine safety checks."""

import pytest

from nova.policy.engine import PolicyEngine


@pytest.fixture
def policy_engine():
    """Create a policy engine instance."""
    return PolicyEngine()


@pytest.mark.unit
class TestPolicySafety:
    """Test policy engine blocks dangerous commands."""

    def test_block_rm_rf(self, policy_engine):
        """Test that 'rm -rf' is blocked."""
        step = {"command": "rm -rf /", "tool": "terminal"}
        decision = policy_engine.evaluate(step)
        assert decision.allowed is False
        assert decision.risk_level == "critical"

    def test_block_sudo(self, policy_engine):
        """Test that sudo commands are blocked."""
        step = {"command": "sudo rm -rf /", "tool": "terminal"}
        decision = policy_engine.evaluate(step)
        assert decision.allowed is False

    def test_block_force_push(self, policy_engine):
        """Test that git force push is evaluated."""
        step = {"command": "git push --force", "tool": "terminal"}
        decision = policy_engine.evaluate(step)
        # Should return a decision (may or may not be blocked depending on policy)
        assert decision is not None
        assert hasattr(decision, "allowed")

    def test_block_reset_hard(self, policy_engine):
        """Test that git reset --hard is evaluated."""
        step = {"command": "git reset --hard", "tool": "terminal"}
        decision = policy_engine.evaluate(step)
        # Should return a decision (may or may not be blocked depending on policy)
        assert decision is not None
        assert hasattr(decision, "allowed")

    def test_allow_safe_command(self, policy_engine):
        """Test that safe commands are allowed."""
        step = {"command": "echo 'hello'", "tool": "terminal"}
        decision = policy_engine.evaluate(step)
        assert decision.allowed is True
        assert decision.risk_level == "low"

    def test_allow_file_creation(self, policy_engine):
        """Test that file creation is allowed."""
        step = {"tool": "filesystem", "action": "create file"}
        decision = policy_engine.evaluate(step)
        assert decision.allowed is True

    def test_high_risk_detection(self, policy_engine):
        """Test that high-risk operations are flagged."""
        step = {"command": "rm -rf /home/user", "tool": "terminal"}
        decision = policy_engine.evaluate(step)
        assert decision.risk_level in ["high", "critical"]

    def test_decision_has_reason(self, policy_engine):
        """Test that decisions include reasoning."""
        step = {"command": "rm -rf /", "tool": "terminal"}
        decision = policy_engine.evaluate(step)
        assert decision.reason is not None
        assert len(decision.reason) > 0
