# NOVA – Neural Orchestrated Virtual Assistant


[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An autonomous DevOps AI agent that turns natural language instructions into structured, secure system actions.

---

## What is NOVA?

NOVA is a locally running AI-powered assistant that understands plain English instructions, generates structured execution plans, validates them for safety, and executes them on your machine.

It is designed as an experiment in building a secure, modular, self-healing DevOps automation agent — fully offline and architecture-driven.

Think of it as:
**"Describe what you want built, and NOVA handles the execution safely."**

---

## What Can NOVA Do?

### 🧠 Plan Generation
- Understands tasks written in plain English
- Breaks them into structured execution steps
- Uses local AI (Ollama) to remain fully offline

### 🔐 Safe Execution
- Executes commands natively or inside Docker
- Blocks dangerous operations automatically
- Validates plans before execution
- Applies timeouts and retry limits

### 🔁 Self-Healing
- Detects failures using return codes
- Captures stdout and stderr
- Attempts automatic correction via LLM
- Logs retry attempts for traceability

### 🗄 Persistent Memory
- Stores sessions in PostgreSQL
- Tracks execution plans (JSONB)
- Logs every step and result
- Maintains retry history

### 📊 Metrics & Risk Management
- Tracks read/write operations per session
- Calculates weighted risk scores
- Adapts operation limits based on recent risk
- Enters strict mode for high-risk patterns

### 🧪 Preview Modes
- **Simulation Mode** (`--simulate`): Shows risk assessment without execution
- **Plan-Only Mode** (`--plan-only`): Shows execution plan without policy checks
- **Diff Preview**: Shows unified diffs for file modifications

---

## How It Works

```
You: "Create a hello world program in Python"
    ↓
Planner (Ollama): Generates structured JSON plan
    ↓
Validator: Ensures schema + tool safety
    ↓
Security Layer: Blocks unsafe commands
    ↓
Policy Engine: Evaluates risk levels
    ↓
Metrics Tracker: Tracks operations & risk score
    ↓
Executor: Runs inside native or Docker sandbox
    ↓
Database: Stores results, metrics & retry history
```

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/hassarch/nova-agent.git
cd nova-agent

# Install in development mode
pip install -e ".[dev]"

# Run migrations
python -m alembic upgrade head
```

### Basic Usage

```bash
# Execute a task
nova run "create a hello world Python script"

# Simulate execution (no changes made)
nova run "create a hello world Python script" --simulate

# Show plan only (skip policy checks)
nova run "create a hello world Python script" --plan-only

# View session history
nova session

# Resume a failed workflow
nova resume <session_id>
```

---

## Execution Modes

### 🚀 Normal Execution
```bash
nova run "create test.py"
```
- ✓ Executes the plan
- ✓ Applies policy checks
- ✓ Tracks metrics
- ✓ Creates files/runs commands

### 🧪 Simulation Mode
```bash
nova run "create test.py" --simulate
```
- ✓ Shows risk levels (GREEN/YELLOW/RED)
- ✓ Displays affected files
- ✓ Shows diff previews for modifications
- ✗ No files created
- ✗ No commands executed

### 📋 Plan-Only Mode
```bash
nova run "create test.py" --plan-only
```
- ✓ Shows execution plan
- ✓ Shows diff previews
- ✗ Skips policy evaluation
- ✗ No files created
- ✗ No commands executed

---

## Metrics & Risk Management

### Risk Scoring Formula

```
risk_score = (read_count × 1) + (write_count × 2) + (retry_count × 3)
```

### Adaptive Limits

- **Default**: 4 operations per session
- **Strict Mode**: 2 operations (triggered when avg risk > 8 in last 3 sessions)

---

## Safety Model

NOVA enforces multiple layers of protection:

- Blocks destructive commands (rm -rf, sudo, shutdown, etc.)
- Validates structured plan schema
- Normalizes hallucinated tools
- Optional Docker sandbox isolation
- CPU & memory limits in container mode
- Execution timeouts
- Retry cap to prevent infinite loops
- Risk-based operation limits
- Policy-driven decision making

The goal is controlled automation — not unrestricted execution.

---

## Database Schema

### Sessions Table (with Metrics)

```sql
sessions
├── id (PK)
├── session_id (UNIQUE)
├── created_at
├── read_count (tracks file reads)
├── write_count (tracks file writes)
├── retry_count (tracks retry attempts)
└── risk_score (calculated risk)
```

### Run Migrations

```bash
python -m alembic upgrade head
```

---

## Architecture

The codebase follows a professional Python package structure:

```
nova/                          ← Repository root
├── nova/                      ← Python package
│   ├── controller/            # Agent orchestration & execution
│   ├── planner/               # Task planning & decomposition
│   ├── policy/                # Security & policy enforcement
│   ├── recovery/              # Failure recovery & resumption
│   ├── analytics/             # Metrics & analysis
│   ├── memory/                # Context & state management
│   ├── database/              # Data persistence
│   ├── execution/             # Command execution strategies
│   ├── security/              # Input validation
│   ├── tools/                 # Tool implementations
│   ├── observability/         # Metrics tracking
│   ├── config/                # Configuration
│   ├── utils/                 # Shared utilities
│   └── main.py                # CLI entry point
├── tests/                     # Test suite
├── migrations/                # Database migrations
└── scripts/                   # Utility scripts
```

For detailed structure documentation, see [STRUCTURE.md](STRUCTURE.md).

---

## Development

### Code Quality

Run all checks:
```bash
bash scripts/run-ci-checks.sh
```

Individual checks:
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
```

### Testing

```bash
# Run all tests
pytest tests -v

# Run unit tests only
pytest tests -m unit -v

# With coverage
pytest tests -v --cov=nova --cov-report=html
```

---

## Tech Stack

- Python 3.11+
- Typer (CLI)
- PostgreSQL
- SQLAlchemy 2.0
- Alembic (migrations)
- Ollama (local LLM runtime)
- Docker (sandbox execution)
- Rich (CLI formatting)
- Difflib (diff generation)

---

## Version

**v0.1.0** – Professional package structure with enhanced CI/CD

Includes:
- Structured planning
- Security validation
- Native + Docker execution
- Self-healing retry loop
- Persistent memory layer
- Metrics tracking & risk scoring
- Adaptive operation limits
- Simulation mode with risk assessment
- Plan-only mode
- Diff preview for modifications
- **NEW: Professional nova/ package structure**
- **NEW: Enhanced CI/CD pipelines**
- **NEW: Type checking with MyPy**
- **NEW: Security scanning with Bandit**

---

## Contributing

This is an experimental project. Contributions welcome for:
- Additional tool integrations
- Enhanced policy rules
- Performance optimizations
- Documentation improvements

---

## License

MIT License - see LICENSE file for details