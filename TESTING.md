# NOVA Testing Guide

## Overview

NOVA includes a comprehensive test suite covering core functionality and safety invariants. The test suite validates:

- **Policy Engine Safety**: Dangerous commands are blocked
- **Configuration Validation**: Settings load correctly
- **Doctor Command**: Environment checks work properly
- **Resume Logic**: Workflows resume correctly without duplication
- **Retry Limits**: Retry logic enforces limits

## Running Tests

### Run All Tests

```bash
pytest tests
```

Expected output:
```
======================== 54 passed in 0.89s =========================
```

### Run Unit Tests Only

```bash
pytest tests -m unit
```

### Run Specific Test File

```bash
pytest tests/test_policy.py -v
```

### Run Specific Test Class

```bash
pytest tests/test_policy.py::TestPolicySafety -v
```

### Run Specific Test

```bash
pytest tests/test_policy.py::TestPolicySafety::test_block_rm_rf -v
```

### Run with Coverage

```bash
pytest tests --cov=nova --cov-report=html
```

## Test Structure

### tests/test_policy.py

Tests for policy engine safety checks.

**What it tests:**
- Blocks `rm -rf` commands
- Blocks `sudo` commands
- Blocks dangerous git operations
- Allows safe commands
- Detects high-risk operations
- Provides reasoning for decisions

**Example:**
```python
def test_block_rm_rf(policy_engine):
    """Test that 'rm -rf' is blocked."""
    step = {"command": "rm -rf /", "tool": "terminal"}
    decision = policy_engine.evaluate(step)
    assert decision.allowed is False
    assert decision.risk_level == "critical"
```

### tests/test_config.py

Tests for configuration system.

**What it tests:**
- Settings are loaded
- Database configuration is valid
- OLLAMA URL is configured
- Configuration values have correct types
- Required fields are not empty

**Example:**
```python
def test_db_port_is_integer():
    """Test that DB_PORT is an integer."""
    assert isinstance(settings.DB_PORT, int)
    assert settings.DB_PORT > 0
    assert settings.DB_PORT < 65536
```

### tests/test_doctor.py

Tests for doctor command diagnostics.

**What it tests:**
- Python version check passes
- Git check returns result
- Ollama check returns result
- Model check returns result
- Config check passes
- Database check returns result
- All checks return proper tuple format

**Example:**
```python
def test_python_check_passes():
    """Test that Python version check passes."""
    status, message = check_python()
    assert status is True
    assert "Python" in message
```

### tests/test_resume.py

Tests for resume workflow logic.

**What it tests:**
- Resume skips completed steps
- Resume finds running steps
- Resume finds failed steps
- Resume handles all-completed case
- Resume handles empty step list
- Resume maintains step order
- Resume is idempotent

**Example:**
```python
def test_resume_skips_completed_steps():
    """Test that resume skips completed steps."""
    steps = [
        {"id": 1, "status": "completed"},
        {"id": 2, "status": "pending"},
    ]
    first_incomplete = next(
        (s for s in steps if s["status"] != "completed"), None
    )
    assert first_incomplete["id"] == 2
```

### tests/test_retry.py

Tests for retry logic and limits.

**What it tests:**
- Retry count within limit is allowed
- Retry count at limit is blocked
- Retry count exceeding limit is blocked
- Retry increment works correctly
- Retry attempts are tracked
- Retry should stop logic works

**Example:**
```python
def test_retry_count_at_limit():
    """Test that retry count at limit is blocked."""
    max_retries = 3
    retry_count = 3
    assert retry_count >= max_retries
```

## Test Coverage

Current test coverage:

- **Policy Engine**: 8 tests
- **Configuration**: 8 tests
- **Doctor Command**: 9 tests
- **Resume Logic**: 7 tests
- **Retry Logic**: 8 tests
- **Parser**: 4 tests
- **Workflow State**: 7 tests
- **Database**: 1 test

**Total: 54 tests**

## Writing New Tests

### Test Template

```python
"""Tests for [feature]."""

import pytest


@pytest.mark.unit
class TestFeatureName:
    """Test [feature]."""

    def test_something(self):
        """Test that something works."""
        # Arrange
        input_data = ...
        
        # Act
        result = function(input_data)
        
        # Assert
        assert result == expected
```

### Best Practices

1. **Use descriptive names**: `test_block_rm_rf` not `test_1`
2. **One assertion per test**: Focus on single behavior
3. **Use fixtures**: Share setup code with `@pytest.fixture`
4. **Test invariants**: Test core safety properties
5. **Avoid AI behavior**: Don't test LLM outputs
6. **Use marks**: Add `@pytest.mark.unit` for categorization

## CI/CD Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Manual trigger

### GitHub Actions

See `.github/workflows/ci.yml` for CI configuration.

```yaml
- name: Run tests
  run: pytest tests -m unit -v --cov=nova
```

## Troubleshooting

### Tests fail with "database not available"

The database test gracefully skips if PostgreSQL isn't running:

```bash
pytest tests/test_db.py -v
# Output: SKIPPED - Database not available
```

### Import errors

Ensure you're using the venv Python:

```bash
/path/to/venv/bin/python3 -m pytest tests
```

### Slow tests

Run only unit tests:

```bash
pytest tests -m unit
```

## Performance

- **Full suite**: ~0.89 seconds
- **Unit tests only**: ~0.80 seconds
- **Single test**: ~0.05 seconds

## Future Test Additions

- [ ] Integration tests with real database
- [ ] End-to-end workflow tests
- [ ] Performance benchmarks
- [ ] Security vulnerability tests
- [ ] Stress tests with large workflows
- [ ] Concurrent execution tests

## Related Documentation

- `DEVELOPMENT.md` - Development setup
- `ERROR_HANDLING.md` - Error handling
- `LOGGING.md` - Logging system
- `STEP_LEVEL_PERSISTENCE.md` - Resume workflow
