# NOVA

**Local Autonomous DevOps AI Runtime**

Installable, offline, policy-governed AI workflow engine.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version 0.1.3](https://img.shields.io/badge/version-0.1.3-green.svg)](CHANGELOG.md)

---

## What is NOVA?

NOVA is a locally running AI-powered assistant that understands plain English instructions, generates structured execution plans, validates them for safety, and executes them on your machine.

It is designed as an experiment in building a secure, modular, self-healing DevOps automation agent — fully offline and architecture-driven.

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

## 🚀 Installation

### Prerequisites
- Python 3.11+
- PostgreSQL (for session persistence)
- Ollama (for local LLM planning)
- Docker (optional, for sandboxed execution)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/nova
cd nova

# Install in development mode
pip install -e .

# Run database migrations
python -m alembic upgrade head

# Verify installation
nova doctor
```

### Configuration

NOVA reads configuration from `~/.nova/config.yaml`:

```yaml
# Database
db_host: localhost
db_port: 5432
db_name: nova_db

# Ollama (local LLM)
ollama_url: http://localhost:11434

# Execution
use_sandbox: false  # Set to true for Docker isolation
max_retries: 3
```

For detailed configuration, see [CONFIG_SYSTEM.md](CONFIG_SYSTEM.md).

## ⚡ Quick Start

```bash
# Initialize configuration
nova init

# Check environment
nova doctor

# Run a simple task
nova run "create a file named hello.txt with content hello world"

# View session history
nova session

# Resume a failed workflow
nova resume <session_id>
```

## 🔒 Security Model

- **Command whitelist enforcement**: Blocks dangerous operations (rm -rf, sudo, etc.)
- **No sudo execution**: Prevents privilege escalation
- **Git governance protection**: Validates git operations
- **Retry limits**: Prevents infinite retry loops (max 3 retries)
- **Execution timeouts**: 30-second timeout per command
- **Optional simulation mode**: Preview changes without execution
- **Policy-driven decisions**: Risk-based operation limits
- **Input validation**: Command security checks before execution

---

## 📋 Logging & Debugging

NOVA creates session logs in `~/.nova/logs/`:

```bash
# View latest session log
tail -f ~/.nova/logs/session_*.log

# Session log format
2026-02-21 11:50:08 | INFO | nova_session_20260221_115008 | NOVA session started
2026-02-21 11:50:08 | INFO | nova_session_20260221_115008 | Executing prompt: create fast api backend
2026-02-21 11:50:54 | INFO | nova_session_20260221_115008 | Task completed successfully
```

Logs include:
- Session start/end timestamps
- Execution prompts and plans
- Step-by-step execution details
- Error messages with full stack traces
- Retry attempts and recovery strategies
- Final metrics (reads, writes, retries, risk score)

---

## 💡 Common Use Cases

### Create a Project Structure
```bash
nova run "create a python project with src/, tests/, and requirements.txt"
```

### Set Up a Backend
```bash
nova run "create a FastAPI backend with main.py, requirements.txt, and docker-compose.yml"
```

### Initialize Git Repository
```bash
nova run "initialize a git repository with .gitignore and initial commit"
```

### Install Dependencies
```bash
nova run "install dependencies from requirements.txt using pip"
```

### Run Tests
```bash
nova run "run pytest tests with coverage report"
```

---

## 🧪 Testing

NOVA includes a comprehensive test suite covering:
- **Policy Engine**: Command safety validation
- **Configuration**: Settings and defaults
- **Doctor Command**: Environment diagnostics
- **Resume Logic**: Workflow resumption
- **Retry Limits**: Failure recovery
- **Workflow State**: Step-level persistence

Run tests:
```bash
# All tests
pytest tests -v

# With coverage
pytest tests -v --cov=nova --cov-report=html

# Specific test file
pytest tests/test_policy.py -v
```

---

## 📚 Documentation

- [CHANGELOG.md](CHANGELOG.md) – Version history and changes
- [STRUCTURE.md](STRUCTURE.md) – Project architecture
- [CONFIG_SYSTEM.md](CONFIG_SYSTEM.md) – Configuration guide
- [DEVELOPMENT.md](DEVELOPMENT.md) – Development setup
- [TESTING.md](TESTING.md) – Testing guide
- [LOGGING.md](LOGGING.md) – Logging system
- [ERROR_HANDLING.md](ERROR_HANDLING.md) – Error handling
- [STEP_LEVEL_PERSISTENCE.md](STEP_LEVEL_PERSISTENCE.md) – Resume workflow

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

**v0.1.3** – Execution fixes and security hardening

Latest improvements:
- ✅ Shell operator support (`&&`, `||`, pipes, redirects)
- ✅ Automatic parent directory creation for nested files
- ✅ Tool validation in planner (prevents invalid tools like `curl`)
- ✅ Session-based logging with dual output (console + file)
- ✅ Crash-safe error boundary with professional error messages
- ✅ Step-level persistence and resume workflow completion
- ✅ Comprehensive test suite (54 tests covering core invariants)
- ✅ Security hardening with Bandit scanning
- ✅ Full CI/CD pipeline (Black, isort, Flake8, MyPy, Pytest)

Previous versions included:
- Structured planning with Ollama
- Security validation and policy enforcement
- Native + Docker execution strategies
- Self-healing retry loop with LLM recovery
- Persistent memory layer with PostgreSQL
- Metrics tracking & risk scoring
- Adaptive operation limits
- Simulation mode with risk assessment
- Plan-only mode
- Diff preview for modifications

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