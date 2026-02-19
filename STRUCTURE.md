# NOVA Repository Structure

## Overview

The repository follows the standard Python package structure with a clear separation between the repository root and the Python package.

```
nova/                          ← Repository root
├── nova/                      ← Python package (importable as `import nova`)
│   ├── __init__.py
│   ├── main.py               ← CLI entry point
│   ├── controller/           ← Agent execution & orchestration
│   │   ├── __init__.py
│   │   ├── controller.py     ← Main AgentController
│   │   ├── dispatcher.py     ← Tool execution dispatcher
│   │   ├── planner.py        ← Plan generation
│   │   ├── parser.py         ← Plan parsing & validation
│   │   └── retry_engine.py   ← Failure recovery
│   ├── planner/              ← Planning & hierarchical decomposition
│   │   ├── __init__.py
│   │   ├── hierarchical_planner.py
│   │   └── models.py
│   ├── policy/               ← Security & policy enforcement
│   │   ├── __init__.py
│   │   ├── engine.py         ← Policy evaluation
│   │   ├── rules.py          ← Risk assessment rules
│   │   └── models.py
│   ├── recovery/             ← Workflow resumption & state management
│   │   ├── __init__.py
│   │   ├── resume_engine.py  ← Resume from failures
│   │   ├── failure_classifier.py
│   │   └── strategy_engine.py
│   ├── analytics/            ← Session analysis & metrics
│   │   ├── __init__.py
│   │   ├── ai_analyzer.py    ← AI-powered analysis
│   │   ├── queries.py        ← Analytics queries
│   │   └── summaries.py
│   ├── memory/               ← Context & memory management
│   │   ├── __init__.py
│   │   ├── collector.py      ← Context collection
│   │   ├── formatter.py      ← Context formatting
│   │   └── models.py
│   ├── database/             ← Database models & connection
│   │   ├── __init__.py
│   │   ├── models.py         ← SQLAlchemy ORM models
│   │   ├── connection.py     ← DB connection setup
│   │   └── base.py           ← Base model class
│   ├── execution/            ← Command execution strategies
│   │   ├── __init__.py
│   │   ├── strategy.py       ← Execution strategy interface
│   │   ├── native_executor.py ← Local execution
│   │   ├── docker_execution.py ← Docker execution
│   │   └── result.py         ← Execution result models
│   ├── security/             ← Security validation
│   │   ├── __init__.py
│   │   └── command_validator.py
│   ├── tools/                ← Tool implementations
│   │   ├── __init__.py
│   │   └── filesystem_tool.py
│   ├── observability/        ← Metrics & monitoring
│   │   ├── __init__.py
│   │   └── metrics_tracker.py
│   ├── config/               ← Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py       ← Environment settings
│   │   └── logging.py        ← Logging configuration
│   └── utils/                ← Utility functions
│       ├── __init__.py
│       ├── tool_registry.py
│       └── tool_normalizer.py
├── tests/                    ← Test suite
│   ├── __init__.py
│   ├── test_parser.py
│   └── test_workflow_state.py
├── migrations/               ← Alembic database migrations
├── scripts/                  ← Utility scripts
│   └── run-ci-checks.sh
├── .github/                  ← GitHub Actions workflows
│   └── workflows/
│       ├── ci.yml           ← Main branch CI
│       └── dev-ci.yml       ← Dev branch CI
├── pyproject.toml           ← Project metadata & dependencies
├── pytest.ini               ← Pytest configuration
├── alembic.ini              ← Alembic configuration
├── Dockerfile               ← Docker image definition
├── docker-compose.yml       ← Docker Compose setup
├── README.md                ← Project documentation
├── DEVELOPMENT.md           ← Development guide
└── requirements.txt         ← Legacy requirements (use pyproject.toml)
```

## Key Design Principles

### 1. **Double "nova/" Structure**
- **Outer `nova/`** = Repository root (where you clone the project)
- **Inner `nova/`** = Python package (what you import with `import nova`)

This is the standard Python packaging convention used by professional projects.

### 2. **Modular Organization**
Each subdirectory represents a distinct responsibility:
- **controller/** - Orchestration and execution flow
- **planner/** - Task planning and decomposition
- **policy/** - Security and risk management
- **recovery/** - Failure handling and resumption
- **analytics/** - Metrics and analysis
- **memory/** - Context and state management
- **database/** - Data persistence
- **execution/** - Command execution strategies
- **security/** - Input validation and security
- **tools/** - Tool implementations
- **observability/** - Monitoring and metrics
- **config/** - Configuration management
- **utils/** - Shared utilities

### 3. **Import Conventions**
All imports use the `nova` package prefix:
```python
from nova.controller.controller import AgentController
from nova.policy.engine import PolicyEngine
from nova.database.models import Session
```

### 4. **Entry Points**
- **CLI**: `nova.main:main` (defined in pyproject.toml)
- **Package**: `import nova` (from nova/__init__.py)

## Installation

```bash
# Development installation
pip install -e ".[dev]"

# Production installation
pip install .
```

## Running Tests

```bash
# All tests
pytest tests -v

# Unit tests only
pytest tests -m unit -v

# With coverage
pytest tests -v --cov=nova --cov-report=html
```

## Code Quality Checks

```bash
# Format code
black nova tests

# Sort imports
isort nova tests

# Lint
flake8 nova tests --max-line-length=127 --extend-ignore=E203,W503

# Type checking
mypy nova --ignore-missing-imports

# Security scanning
bandit -r nova -ll

# Run all checks
bash scripts/run-ci-checks.sh
```

## Migration from `app/` to `nova/`

The codebase was reorganized from the old `app/` structure to the professional `nova/` package structure:

- All imports updated from `app.*` to `nova.*`
- Old `app/agent/` → `nova/controller/`
- Old `app/core/planning/` → `nova/planner/`
- Old `app/core/policy/` → `nova/policy/`
- Old `app/core/recovery/` → `nova/recovery/`
- Old `app/core/analytics/` → `nova/analytics/`
- Old `app/core/context/` → `nova/memory/`
- All other modules moved to their respective nova/ subdirectories
- CI workflows updated to reference `nova/` instead of `app/`
