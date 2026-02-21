# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2026-02-21

### Added
- Python packaging with CLI entry point (`nova` command)
- Config system (`~/.nova/config.yaml`) with environment validation
- `nova doctor` command for environment diagnostics
- Session-based logging with dual output (console + file)
- Crash-safe error boundary with professional error messages
- Step-level persistence and resume workflow completion
- Comprehensive test suite (54 tests covering core invariants)
- Shell operator support in terminal commands (`&&`, `||`, pipes, etc.)
- Automatic parent directory creation for file operations
- Tool validation in planner with explicit allowed tools list

### Improved
- CLI UX clarity with structured output formatting
- Open-source project structure and documentation
- Reliability and persistence with database-backed state tracking
- Error handling with full stack traces in session logs
- Planner prompt to enforce tool constraints

### Fixed
- Edge-case session persistence issues
- Missing parent directories when creating nested files
- Invalid tool generation by LLM (curl → terminal)
- Shell operator parsing in command execution
- File creation in non-existent directories

## [0.1.2] - 2026-02-15

### Added
- Initial database schema with sessions and execution tracking
- Policy engine for command safety validation
- Retry engine with LLM-based recovery strategies
- Docker execution support
- Filesystem tool for file operations

### Improved
- Command validation and security checks
- Execution result tracking and metrics

## [0.1.1] - 2026-02-10

### Added
- Basic CLI structure
- Ollama integration for LLM planning
- Hierarchical task planning

## [0.1.0] - 2026-02-05

### Added
- Initial project setup
- Core architecture and module structure
