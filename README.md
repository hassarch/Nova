# NOVA – Neural Orchestrated Virtual Assistant

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

## Execution Modes

### 🚀 Normal Execution
```bash
./nova run "create test.py"
```
- ✓ Executes the plan
- ✓ Applies policy checks
- ✓ Tracks metrics
- ✓ Creates files/runs commands

### 🧪 Simulation Mode
```bash
./nova run "create test.py" --simulate
```
- ✓ Shows risk levels (GREEN/YELLOW/RED)
- ✓ Displays affected files
- ✓ Shows diff previews for modifications
- ✗ No files created
- ✗ No commands executed

### 📋 Plan-Only Mode
```bash
./nova run "create test.py" --plan-only
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

```
app/
├── agent/              # Planning, retry engine, orchestration
├── execution/          # Native & Docker executors
├── security/           # Command validation layer
├── tools/              # Filesystem & tool-specific logic
├── database/           # PostgreSQL models & connection
├── config/             # Environment configuration
├── core/
│   ├── policy/         # Risk evaluation & policy engine
│   └── context/        # Context collection & formatting
├── observability/      # Metrics tracking
└── main.py             # CLI entrypoint
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

**v0.1.1** – Enhanced with metrics, risk management, and preview modes

Includes:
- Structured planning
- Security validation
- Native + Docker execution
- Self-healing retry loop
- Persistent memory layer
- **NEW: Metrics tracking & risk scoring**
- **NEW: Adaptive operation limits**
- **NEW: Simulation mode with risk assessment**
- **NEW: Plan-only mode**
- **NEW: Diff preview for modifications**

---

## Contributing

This is an experimental project. Contributions welcome for:
- Additional tool integrations
- Enhanced policy rules
- Performance optimizations
- Documentation improvements

