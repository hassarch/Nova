# NOVA Setup Guide

This guide will help you get NOVA running on your machine in under 5 minutes.

## Prerequisites

- **Python 3.11 or higher** (check: `python3 --version`)
- **Git** (check: `git --version`)
- **Optional:** PostgreSQL, Ollama (for advanced features)

## Quick Setup

### 1. Clone and Navigate

```bash
cd /Users/donut/Desktop/Dev/NOVA
# Or wherever you cloned the repository
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Important:** Always activate the virtual environment before working with NOVA!

### 3. Install Dependencies

```bash
pip install -e ".[dev]"
```

This installs NOVA and all development tools (pytest, black, flake8, etc.).

### 4. Set Up Database

#### Option A: SQLite (Easiest - No Setup Required)

Just skip the PostgreSQL setup! NOVA automatically uses SQLite if PostgreSQL is not configured.

```bash
# Remove or don't create .env file
# NOVA will use nova.db automatically
alembic upgrade head
```

#### Option B: PostgreSQL (For Production)

```bash
# 1. Install PostgreSQL (if not installed)
brew install postgresql  # macOS
# or: sudo apt-get install postgresql  # Ubuntu

# 2. Create database and user
createdb nova_db
createuser nova_user -P  # Enter password when prompted

# 3. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 4. Run migrations
alembic upgrade head
```

### 5. Verify Installation

```bash
nova doctor
```

Expected output:
```
✔ Python 3.x.x
✔ Git installed
✔ Database connection
⚠ Ollama (optional)
⚠ Model 'llama3' (optional)
```

### 6. Run Your First Command

```bash
nova run "create a file called hello.txt with the text 'Hello NOVA'"
```

## Optional: Set Up AI Planning (Ollama)

If you want NOVA to generate execution plans using AI:

```bash
# 1. Install Ollama
# Visit: https://ollama.ai/download

# 2. Start Ollama server (in one terminal)
ollama serve

# 3. Pull the model (in another terminal)
ollama pull llama3

# 4. Test it
nova doctor  # Should now show ✔ for Ollama
```

## Common Commands

```bash
# See all commands
nova --help

# Check environment
nova doctor

# View session history
nova session

# Show version
nova version
```

## Development Workflow

```bash
# Activate venv (always do this first!)
source venv/bin/activate

# Run tests
make test

# Format code
make format

# Run all CI checks
make ci-check

# See all make commands
make help
```

## Troubleshooting

### "command not found: nova"

**Solution:** Activate the virtual environment:
```bash
source venv/bin/activate
```

### "ModuleNotFoundError"

**Solution:** Install dependencies:
```bash
pip install -e ".[dev]"
```

### "Database connection failed"

**Solution:** Use SQLite instead - just remove `.env` file and run:
```bash
alembic upgrade head
```

### "externally-managed-environment"

**Solution:** Use a virtual environment (see step 2 above).

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [DEVELOPMENT.md](DEVELOPMENT.md) for contribution guidelines
- See [STRUCTURE.md](STRUCTURE.md) to understand the codebase
- Review [CONFIG_SYSTEM.md](CONFIG_SYSTEM.md) for configuration options

## Getting Help

- Run `nova --help` for CLI help
- Run `nova doctor` to diagnose issues
- Check the [Troubleshooting](#troubleshooting) section above
- Open an issue on GitHub

---

**Happy automating with NOVA! 🚀**
