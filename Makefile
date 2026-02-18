.PHONY: help install install-dev test lint format type-check security clean docker-build docker-run ci-check pre-commit-install

help:
	@echo "NOVA Agent - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install              Install production dependencies"
	@echo "  make install-dev          Install development dependencies"
	@echo "  make pre-commit-install   Install pre-commit hooks"
	@echo ""
	@echo "Development:"
	@echo "  make lint                 Run linting (flake8)"
	@echo "  make format               Format code (black, isort)"
	@echo "  make type-check           Run type checking (mypy)"
	@echo "  make test                 Run unit tests"
	@echo "  make test-cov             Run tests with coverage"
	@echo "  make security             Run security checks"
	@echo ""
	@echo "CI/CD:"
	@echo "  make ci-check             Run all CI checks locally"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build         Build Docker image"
	@echo "  make docker-run           Run Docker container"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean                Remove build artifacts and cache"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

pre-commit-install:
	pre-commit install

lint:
	flake8 app tests --max-line-length=127 --extend-ignore=E203,W503

format:
	black app tests
	isort app tests

type-check:
	mypy app --ignore-missing-imports

test:
	pytest tests -m unit -v

test-cov:
	pytest tests -m unit -v --cov=app --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

security:
	bandit -r app -ll
	safety check

ci-check:
	bash scripts/run-ci-checks.sh

docker-build:
	docker build -t nova-agent:dev .

docker-run:
	docker run -it --env-file .env nova-agent:dev

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build dist .coverage htmlcov .mypy_cache .pytest_cache
	@echo "Cleaned up build artifacts"

.DEFAULT_GOAL := help
