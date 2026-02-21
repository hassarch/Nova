"""Tests for doctor command diagnostics."""

import pytest

from nova.system.doctor import check_config, check_database, check_git, check_model, check_ollama, check_python


@pytest.mark.unit
class TestDoctorChecks:
    """Test individual doctor checks."""

    def test_python_check_passes(self):
        """Test that Python version check passes."""
        status, message = check_python()
        assert status is True
        assert "Python" in message
        assert "3." in message

    def test_python_check_returns_version(self):
        """Test that Python check returns version info."""
        status, message = check_python()
        assert status is True
        assert len(message) > 0

    def test_git_check_returns_result(self):
        """Test that Git check returns a result."""
        status, message = check_git()
        assert isinstance(status, bool)
        assert isinstance(message, str)
        assert len(message) > 0

    def test_git_check_graceful_failure(self):
        """Test that Git check fails gracefully if not installed."""
        status, message = check_git()
        # Either passes or fails gracefully
        assert isinstance(status, bool)
        if not status:
            assert "not found" in message.lower() or "not installed" in message.lower()

    def test_ollama_check_returns_result(self):
        """Test that Ollama check returns a result."""
        status, message = check_ollama()
        assert isinstance(status, bool)
        assert isinstance(message, str)
        assert len(message) > 0

    def test_model_check_returns_result(self):
        """Test that model check returns a result."""
        status, message = check_model()
        assert isinstance(status, bool)
        assert isinstance(message, str)
        assert len(message) > 0

    def test_config_check_passes(self):
        """Test that config check passes."""
        status, message = check_config()
        assert status is True
        assert len(message) > 0

    def test_database_check_returns_result(self):
        """Test that database check returns a result."""
        status, message = check_database()
        assert isinstance(status, bool)
        assert isinstance(message, str)
        assert len(message) > 0

    def test_check_returns_tuple(self):
        """Test that all checks return tuples."""
        checks = [
            check_python(),
            check_git(),
            check_ollama(),
            check_model(),
            check_config(),
            check_database(),
        ]
        for check in checks:
            assert isinstance(check, tuple)
            assert len(check) == 2
            assert isinstance(check[0], bool)
            assert isinstance(check[1], str)
