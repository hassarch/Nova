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
Executor: Runs inside native or Docker sandbox
    ↓
Database: Stores results & retry history
```

---

## Getting Started (Internal Setup)

### Prerequisites

- Python 3.11+
- PostgreSQL
- Ollama (running locally)
- Docker (optional but recommended)



## Safety Model

NOVA enforces multiple layers of protection:

- Blocks destructive commands (rm -rf, sudo, shutdown, etc.)
- Validates structured plan schema
- Normalizes hallucinated tools
- Optional Docker sandbox isolation
- CPU & memory limits in container mode
- Execution timeouts
- Retry cap to prevent infinite loops

The goal is controlled automation — not unrestricted execution.

---

## Architecture

```
app/
├── agent/          # Planning, retry engine, orchestration
├── execution/      # Native & Docker executors
├── security/       # Command validation layer
├── tools/          # Filesystem & tool-specific logic
├── database/       # PostgreSQL models & connection
├── config/         # Environment configuration
└── main.py         # CLI entrypoint
```

---

## Tech Stack

- Python 3.11+
- Typer (CLI)
- PostgreSQL
- SQLAlchemy 2.0
- Alembic
- Ollama (local LLM runtime)
- Docker (sandbox execution)
- Rich (CLI formatting)

---

## Version

**v0.1.0** – Core autonomous engine

Includes:
- Structured planning
- Security validation
- Native + Docker execution
- Self-healing retry loop
- Persistent memory layer
