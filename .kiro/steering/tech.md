# Technology Stack

## Core Technologies
- **Python 3.11+**: Primary backend language
- **RTL-SDR V4**: RF hardware for signal capture
- **Raspberry Pi Pico W**: MicroPython TCP client for alerts
- **Rich**: Terminal UI library for CLI dashboard
- **NumPy**: Signal processing and analysis

## Build System & Package Management
- **UV**: Modern Python package manager (preferred)
- **pip**: Fallback package manager
- **pyproject.toml**: Modern Python project configuration
- **requirements.txt**: Legacy dependency specification

## Key Libraries & Frameworks
- **FastAPI**: Web framework (for future API expansion)
- **Pydantic**: Data validation and settings management
- **aiohttp**: Async HTTP client
- **Motor/PyMongo**: MongoDB async driver (for future database integration)
- **pytest**: Testing framework with asyncio support

## Development Tools
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest-cov**: Test coverage

## Common Commands

### Environment Setup
```bash
# Using UV (preferred)
uv venv
uv pip install -r requirements.txt

# Using pip
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Running the System
```bash
# Start RTL-SDR server and signal processing
python rtl_sdr/rtl_tcp_server.py
python rtl_sdr/signal_bridge.py

# Or use startup script
python rtl_sdr/startup_server.py

# Run CLI dashboard (live mode)
python cli_dashboard.py --source tcp --tcp-host localhost --tcp-port 8888

# Run CLI dashboard (demo/mock mode)
python cli_dashboard.py --mock
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Only integration tests
pytest -m hardware    # Only hardware tests
```

### Hardware Tools
```bash
# Test RTL-SDR connection
rtl_test

# Manual RTL-TCP server (port 1234)
rtl_tcp -a 127.0.0.1 -p 1234
```

## Architecture Notes
- **No database required**: TCP streaming for MVP
- **Port conventions**: RTL-TCP on 1234, event server on 8888
- **Async-first**: Use asyncio for I/O operations
- **Type hints**: Use Pydantic models for data structures
- **Error handling**: Graceful degradation and logging