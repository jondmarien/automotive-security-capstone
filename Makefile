# Automotive Security Capstone Project Makefile
# All commands use UV for package management and execution

# Runner command - change this if you want to use a different runner
UV_RUN = uv run

.PHONY: run lint type test format clean install dev help

# Default target - run CLI dashboard with mock and synthetic modes
run:
	cd backend && $(UV_RUN) python cli_dashboard.py --mock --synthetic

# Linting with ruff
lint:
	cd backend && $(UV_RUN) ruff check .

# Type checking with ty (astral-sh/ty)
type:
	cd backend && $(UV_RUN) ty check

# Run tests with pytest
test:
	cd backend && $(UV_RUN) pytest

# Format code with ruff formatter
format:
	cd backend && $(UV_RUN) ruff format .

# Fix linting issues automatically
lint-fix:
	cd backend && $(UV_RUN) ruff check --fix .

# Run all quality checks (lint, type, test)
check: lint type test

# Install dependencies
install:
	cd backend && uv pip install -r requirements.txt

# Install development dependencies
dev:
	cd backend && uv pip install -r requirements.txt -r requirements-dev.txt

# Run the complete system with hardware detection
hardware:
	cd backend && $(UV_RUN) python real_hardware_launcher.py

# Run CLI dashboard in different modes
demo:
	cd backend && $(UV_RUN) python cli_dashboard.py --mock

synthetic:
	cd backend && $(UV_RUN) python cli_dashboard.py --synthetic

# Validate detection accuracy
validate:
	cd backend && $(UV_RUN) python utils/validate_detection_accuracy.py

# Deploy to Pico W
deploy-pico:
	cd backend && $(UV_RUN) python deploy_pico.py

# Clean up temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type f -name ".coverage" -delete

# Show available commands
help:
	@echo "Available commands:"
	@echo "  run          - Run CLI dashboard with mock and synthetic modes (default)"
	@echo "  lint         - Run ruff linting"
	@echo "  type         - Run ty type checking"
	@echo "  test         - Run pytest tests"
	@echo "  format       - Format code with ruff"
	@echo "  lint-fix     - Fix linting issues automatically"
	@echo "  check        - Run all quality checks (lint, type, test)"
	@echo "  install      - Install dependencies"
	@echo "  dev          - Install development dependencies"
	@echo "  hardware     - Run complete system with hardware detection"
	@echo "  demo         - Run CLI dashboard in mock mode"
	@echo "  synthetic    - Run CLI dashboard in synthetic mode"
	@echo "  validate     - Validate detection accuracy"
	@echo "  deploy-pico  - Deploy to Pico W"
	@echo "  clean        - Clean up temporary files"
	@echo "  help         - Show this help message"
