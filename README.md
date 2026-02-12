# NOVA - Neural Orchestrated Virtual Assistant

An AI-powered agent that generates and executes plans based on natural language prompts.

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd NOVA
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Start services**
   ```bash
   # Terminal 1: Start PostgreSQL
   docker run --name nova-postgres -e POSTGRES_PASSWORD=nova_password -e POSTGRES_USER=nova_user -e POSTGRES_DB=nova_db -p 5432:5432 postgres:15

   # Terminal 2: Start Ollama
   ollama serve

   # Terminal 3: Pull the model
   ollama pull llama3
   ```

4. **Run migrations**
   ```bash
   alembic upgrade head
   ```

5. **Use NOVA**
   ```bash
   nova "create a simple python hello world program"
   ```

### Docker Compose

```bash
docker-compose up
```

## Usage

```bash
nova "your prompt here"
```

Examples:
- `nova "create a simple python hello world program"`
- `nova "write a bash script to backup files"`
- `nova "create a REST API endpoint"`

## Development

### Run Tests
```bash
pytest tests/ -v
```

### Run Linting
```bash
flake8 app
black app
isort app
```

### Pre-commit Hooks
```bash
pre-commit install
pre-commit run --all-files
```

## CI/CD Pipeline

The project uses GitHub Actions for:
- **Testing**: Unit tests with pytest
- **Linting**: Code quality checks with flake8
- **Type Checking**: Static type analysis with mypy
- **Building**: Package building
- **Deployment**: Automated deployment to production

## Architecture

- **Agent Controller**: Orchestrates the workflow
- **Planner**: Generates execution plans using Ollama
- **Parser**: Validates and parses plans
- **Dispatcher**: Routes and executes plan steps
- **Executor**: Runs terminal and filesystem operations

## Database

Uses PostgreSQL with Alembic for migrations.

## Environment Variables

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nova_db
DB_USER=nova_user
DB_PASSWORD=nova_password
OLLAMA_URL=http://localhost:11434
```

## License

MIT
