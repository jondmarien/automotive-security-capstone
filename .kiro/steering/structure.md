# Project Structure

## Root Directory Layout
```
├── backend/                  # Main Python backend code
├── .kiro/                   # Kiro IDE configuration and steering
├── .vscode/                 # VS Code configuration
├── .git/                    # Git repository
└── README.md                # Project overview and quick start
```

## Backend Directory Organization
```
backend/
├── cli_dashboard.py              # Rich-based CLI dashboard (main UI)
├── cli_dashboard_detection_adapter.py  # Dashboard detection integration
├── detection/                    # Event detection and analysis logic
│   ├── event_logic.py           # Core event detection algorithms
│   ├── packet.py                # Packet structure definitions
│   ├── security_analyzer.py     # Security threat analysis
│   ├── security_report.py       # Report generation
│   └── threat_levels.py         # Threat classification system
├── rtl_sdr/                     # RTL-SDR hardware integration
│   ├── rtl_tcp_server.py        # RTL-SDR TCP server management
│   ├── signal_bridge.py         # Signal processing and event bridge
│   ├── startup_server.py        # System startup orchestration
│   └── recordings/              # Signal recordings for testing
├── pico/                        # Raspberry Pi Pico W client code
│   ├── main.py                  # MicroPython TCP client
│   └── NFC_PN532.py            # NFC hardware interface
├── hardware/                    # Hardware abstraction layer
│   └── mock/                    # Mock hardware for testing
├── docs/                        # Project documentation
│   ├── diagrams/               # Architecture diagrams
│   ├── plans/                  # Project planning documents
│   ├── detection_logic_explained.md  # Detection algorithm docs
│   ├── migration_plan.md       # Development roadmap
│   └── poc_migration_plan.md   # POC implementation guide
├── rtl_sdr_bin/                # RTL-SDR Windows binaries
└── [config files]             # pyproject.toml, requirements.txt, etc.
```

## File Naming Conventions
- **Snake_case**: All Python files and directories
- **Descriptive names**: Files clearly indicate their purpose
- **Module organization**: Related functionality grouped in directories
- **Main entry points**: Key scripts at backend root level

## Key Entry Points
- `cli_dashboard.py`: Main user interface and demo tool
- `rtl_sdr/startup_server.py`: System startup orchestration
- `rtl_sdr/rtl_tcp_server.py`: Hardware server management
- `pico/main.py`: Pico W client firmware

## Configuration Files
- `pyproject.toml`: Modern Python project configuration
- `requirements.txt`: Python dependencies
- `pytest.ini`: Test configuration
- `.env.example`: Environment variable template
- `.gitignore`: Git ignore patterns

## Directory Purposes
- **detection/**: Core security analysis and threat detection logic
- **rtl_sdr/**: Hardware interface and signal processing
- **pico/**: MicroPython code for Raspberry Pi Pico W
- **hardware/**: Hardware abstraction and mocking
- **docs/**: All project documentation and planning
- **rtl_sdr_bin/**: Windows RTL-SDR binaries for development

## Code Organization Principles
- **Separation of concerns**: Hardware, detection, UI in separate modules
- **Single responsibility**: Each file has a clear, focused purpose
- **Layered architecture**: Hardware → Processing → Detection → UI
- **Mock-friendly**: Hardware abstraction enables testing without devices
- **Documentation co-located**: Docs directory contains all project documentation