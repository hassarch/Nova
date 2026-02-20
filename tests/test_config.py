"""Tests for configuration system."""

import pytest

from nova.config.settings import settings


@pytest.mark.unit
class TestConfigDefaults:
    """Test configuration defaults."""

    def test_settings_loaded(self):
        """Test that settings are loaded."""
        assert settings is not None

    def test_db_host_configured(self):
        """Test that database host is configured."""
        # Skip if not configured (CI environment)
        if settings.DB_HOST is None:
            pytest.skip("DB_HOST not configured in environment")
        assert settings.DB_HOST is not None
        assert isinstance(settings.DB_HOST, str)

    def test_db_port_configured(self):
        """Test that database port is configured."""
        # Skip if not configured (CI environment)
        if settings.DB_PORT is None:
            pytest.skip("DB_PORT not configured in environment")
        assert settings.DB_PORT is not None
        assert isinstance(settings.DB_PORT, int)

    def test_db_name_configured(self):
        """Test that database name is configured."""
        # Skip if not configured (CI environment)
        if settings.DB_NAME is None:
            pytest.skip("DB_NAME not configured in environment")
        assert settings.DB_NAME is not None
        assert isinstance(settings.DB_NAME, str)

    def test_use_sandbox_configured(self):
        """Test that USE_SANDBOX is configured."""
        assert hasattr(settings, "USE_SANDBOX")
        assert isinstance(settings.USE_SANDBOX, bool)

    def test_ollama_url_configured(self):
        """Test that OLLAMA_URL is configured."""
        assert settings.OLLAMA_URL is not None
        assert isinstance(settings.OLLAMA_URL, str)
        assert settings.OLLAMA_URL.startswith("http")


@pytest.mark.unit
class TestConfigValidation:
    """Test configuration validation."""

    def test_db_port_is_integer(self):
        """Test that DB_PORT is an integer."""
        # Skip if not configured (CI environment)
        if settings.DB_PORT is None:
            pytest.skip("DB_PORT not configured in environment")
        assert isinstance(settings.DB_PORT, int)
        assert settings.DB_PORT > 0
        assert settings.DB_PORT < 65536

    def test_db_host_not_empty(self):
        """Test that DB_HOST is not empty."""
        # Skip if not configured (CI environment)
        if settings.DB_HOST is None:
            pytest.skip("DB_HOST not configured in environment")
        assert len(settings.DB_HOST) > 0

    def test_db_name_not_empty(self):
        """Test that DB_NAME is not empty."""
        # Skip if not configured (CI environment)
        if settings.DB_NAME is None:
            pytest.skip("DB_NAME not configured in environment")
        assert len(settings.DB_NAME) > 0

    def test_ollama_url_valid_format(self):
        """Test that OLLAMA_URL has valid format."""
        url = settings.OLLAMA_URL
        assert url.startswith("http://") or url.startswith("https://")
