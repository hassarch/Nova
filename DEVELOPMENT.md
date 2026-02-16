# Development Guide

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Ollama (for LLM integration)
- Git

### Local Development Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd nova-agent
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -e ".[dev]"
```

4. **Setup pre-commit hooks**

```bash
pre-commit install
```

5. **Configure environment**

```bash
cp .env.example .env
# Edit .env with your settings
```

6. **Setup database**

```bash
# Create PostgreSQL database
createdb nova_db -U nova_user

# Run migrations
python -m alembic upgrade head
```

7. **Start Ollama** (in separate terminal)

```bash
ollama serve
```

## Development Workflow

### Before committing

1. **Run pre-commit hooks**

```bash
pre-commit run --all-files
```

2. **Run tests**

```bash
pytest tests -v
```

3. **Check coverage**

```bash
pytest tests --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

### Code style

- **Formatting**: Black (line length: 127)
- **Imports**: isort with Black profile
- **Linting**: Flake8
- **Type hints**: MyPy (non-blocking)

### Running tests

```bash
# All tests
pytest tests -v

# Unit tests only
pytest tests -m unit -v

# Integration tests only
pytest tests -m integration -v

# Specific test file
pytest tests/test_parser.py -v

# With coverage
pytest tests --cov=app --cov-report=term-missing
```

### Debugging

```bash
# Run with verbose output
pytest tests -vv -s

# Run specific test with debugging
pytest tests/test_parser.py::test_validate -vv -s

# Drop into debugger on failure
pytest tests --pdb
```

## Project Structure

```
nova-agent/
├── app/
│   ├── agent/              # Agent orchestration
│   ├── core/               # Core functionality
│   ├── database/           # Database models
│   ├── execution/          # Execution engines
│   ├── security/           # Security validators
│   ├── tools/              # Tool implementations
│   ├── config/             # Configuration
│   ├── observability/      # Metrics & monitoring
│   └── main.py             # CLI entry point
├── tests/                  # Test suite
├── migrations/             # Database migrations
├── .github/workflows/      # CI/CD pipelines
├── Dockerfile              # Docker configuration
├── requirements.txt        # Dependencies
├── pyproject.toml          # Project metadata
└── README.md               # Project documentation
```

## Common Tasks

### Add a new dependency

```bash
# Add to requirements.txt or pyproject.toml
pip install <package>
pip freeze > requirements.txt
```

### Create a database migration

```bash
python -m alembic revision --autogenerate -m "Description of changes"
python -m alembic upgrade head
```

### Run the CLI locally

```bash
python nova run "Your task here"
python nova run "Your task here" --simulate
python nova session
```

### Build Docker image

```bash
docker build -t nova-agent:dev .
docker run -it nova-agent:dev
```

## Troubleshooting

### Database connection errors

```bash
# Check PostgreSQL is running
psql -U nova_user -d nova_db -c "SELECT 1"

# Reset database
dropdb nova_db -U nova_user
createdb nova_db -U nova_user
python -m alembic upgrade head
```

### Import errors

```bash
# Reinstall package in development mode
pip install -e .
```

### Pre-commit hook failures

```bash
# Run specific hook
pre-commit run black --all-files
pre-commit run isort --all-files

# Skip hooks temporarily
git commit --no-verify
```

### Tests fail with "database does not exist"

```bash
# Ensure database is created and migrations are run
createdb nova_db -U nova_user
python -m alembic upgrade head
```

## CI/CD

The project uses GitHub Actions for CI/CD. See `.github/workflows/README.md` for details.

### Local CI simulation

```bash
# Run all checks that CI runs
bash scripts/run-ci-checks.sh
```

## Contributing

1. Create a feature branch from `dev`
2. Make your changes
3. Run tests and linting
4. Commit with clear messages
5. Push and create a pull request
6. Wait for CI to pass
7. Request review

## Resources

- [Python Best Practices](https://pep8.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
