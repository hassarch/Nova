#!/bin/bash

# CI Checks Script
# Runs all checks that the CI pipeline runs locally

set -e

echo "🔍 Running CI Checks..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
FAILED=0

# Determine Python command
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Function to run a check
run_check() {
    local name=$1
    local command=$2
    
    echo -e "${YELLOW}Running: $name${NC}"
    if eval "$command"; then
        echo -e "${GREEN}✓ $name passed${NC}"
    else
        echo -e "${RED}✗ $name failed${NC}"
        FAILED=$((FAILED + 1))
    fi
    echo ""
}

# Check if dev dependencies are installed
if ! $PYTHON_CMD -c "import black" 2>/dev/null; then
    echo -e "${YELLOW}Installing dev dependencies...${NC}"
    $PYTHON_CMD -m pip install -e ".[dev]"
    echo ""
fi

# Run checks
run_check "Black (formatting)" "black --check nova tests"
run_check "isort (import sorting)" "isort --check-only nova tests"
run_check "Flake8 (linting)" "flake8 nova tests --max-line-length=127 --extend-ignore=E203,W503"

# MyPy is non-blocking (optional type checking)
echo -e "${YELLOW}Running: MyPy (type checking)${NC}"
if mypy nova --ignore-missing-imports 2>&1 | head -20; then
    echo -e "${GREEN}✓ MyPy (type checking) passed${NC}"
else
    echo -e "${YELLOW}⚠ MyPy (type checking) has warnings (non-blocking)${NC}"
fi
echo ""

# Pytest with coverage
if $PYTHON_CMD -c "import pytest" 2>/dev/null; then
    echo -e "${YELLOW}Running: Pytest (unit tests with coverage)${NC}"
    if pytest tests -m unit -v --tb=short --cov=nova --cov-report=term-missing 2>&1 | tail -15; then
        echo -e "${GREEN}✓ Pytest (unit tests) passed${NC}"
    else
        echo -e "${RED}✗ Pytest (unit tests) failed${NC}"
        FAILED=$((FAILED + 1))
    fi
    echo ""
else
    echo -e "${YELLOW}Skipping tests (pytest not installed)${NC}"
fi

# Summary
echo ""
echo "================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ $FAILED check(s) failed${NC}"
    echo ""
    echo "To fix formatting issues, run:"
    echo "  black nova tests"
    echo "  isort nova tests"
    exit 1
fi
