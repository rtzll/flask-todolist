# Flask-Todolist — task runner
# Requires: https://github.com/casey/just

set dotenv-load := false

# List all available recipes
[private]
default:
    @just --list

# Run the full local CI gate (lint, format, typecheck, deps, test)
check:
    just lint
    just format-check
    just typecheck
    just deps
    just test

# Run the test suite
test:
    uv run pytest -v

# Run ruff linter
lint:
    uv run ruff check .

# Run ruff linter with auto-fix
fix:
    uv run ruff check --fix .
    uv run ruff format .

# Check formatting without modifying files
format-check:
    uv run ruff format --check .

# Format all files
format:
    uv run ruff format .

# Run ty type checker
typecheck:
    uv run ty check

# Run deptry dependency check
deps:
    uv run deptry .

# Upgrade all dependencies and sync
update:
    uv lock --upgrade
    uv sync

# Run the Flask development server
run:
    APP_CONFIG=development uv run flask run

# Open a Flask shell
shell:
    uv run flask shell

# Fill the database with fake data
db:
    uv run flask fill-db

# Clean generated/cache directories
clean:
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type d -name ".pytest_cache" -exec rm -rf {} +
    find . -type d -name ".ruff_cache" -exec rm -rf {} +
    find . -type d -name ".mypy_cache" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
