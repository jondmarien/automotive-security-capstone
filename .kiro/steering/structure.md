# Project Structure & Architecture Guide

## Root Directory Layout & Organization Philosophy

```
automotive-security-capstone/
├── backend/                  # Main Python backend code (core system)
├── .kiro/                   # Kiro IDE configuration and steering rules
├── .vscode/                 # VS Code configuration and debugging setup
├── .git/                    # Git repository with comprehensive history
└── README.md                # Project overview, quick start, and setup guide
```

### Directory Design Principles
- **Monorepo Structure**: Single repository contains all project components
- **Clear Separation**: Each top-level directory has distinct responsibility
- **IDE Integration**: Configuration for multiple development environments
- **Documentation First**: README provides immediate project understanding

## Backend Directory Deep Dive

### Complete Backend Structure
```
backend/
├── cli_dashboard.py                      # Rich-based CLI dashboard (main UI entry point)
├── cli_dashboard_detection_adapter.py   # Dashboard-detection system integration layer
├── detection/                           # Core security analysis and threat detection
│   ├── __init__.py                     # Package initialization and exports
│   ├── event_logic.py                  # Core event detection algorithms and heuristics
│   ├── packet.py                       # RF packet structure definitions and parsing
│   ├── security_analyzer.py            # Main security threat analysis engine
│   ├── security_report.py              # Report generation and formatting
│   └── threat_levels.py                # Threat classification system (BENIGN/SUSPICIOUS/MALICIOUS)
├── rtl_sdr/                            # RTL-SDR hardware integration and signal processing
│   ├── __init__.py                     # RTL-SDR package initialization
│   ├── rtl_tcp_server.py               # RTL-SDR TCP server management and control
│   ├── signal_bridge.py                # Signal processing and event bridge to detection
│   ├── startup_server.py               # System startup orchestration and health checks
│   └── recordings/                     # Pre-recorded RF signals for testing and demos
│       ├── key_fob_315mhz.iq          # Sample key fob signals
│       ├── tpms_433mhz.iq             # TPMS sensor data
│       └── jamming_attack.iq          # Simulated jamming attack
├── pico/                               # Raspberry Pi Pico W embedded client code
│   ├── main.py                         # MicroPython TCP client and alert system
│   ├── NFC_PN532.py                   # NFC/RFID hardware interface library
│   ├── config.py                      # Pico W configuration and network settings
│   └── led_controller.py              # LED alert system controller
├── hardware/                           # Hardware abstraction layer and interfaces
│   ├── __init__.py                     # Hardware package initialization
│   ├── rtl_sdr_interface.py           # RTL-SDR hardware abstraction
│   ├── pico_interface.py              # Pico W communication interface
│   └── mock/                          # Mock hardware implementations for testing
│       ├── __init__.py                # Mock package initialization
│       ├── mock_rtl_sdr.py           # Simulated RTL-SDR for development
│       ├── mock_pico.py              # Simulated Pico W for testing
│       └── signal_generator.py        # Synthetic RF signal generation
├── utils/                              # Shared utilities and helper functions
│   ├── __init__.py                     # Utils package initialization
│   ├── logging_config.py              # Centralized logging configuration
│   ├── config_manager.py              # Configuration file management
│   ├── signal_processing.py           # Common signal processing functions
│   └── network_utils.py               # Network communication utilities
├── tests/                              # Comprehensive test suite
│   ├── __init__.py                     # Test package initialization
│   ├── conftest.py                     # Pytest configuration and fixtures
│   ├── test_detection/                 # Detection system tests
│   │   ├── test_event_logic.py        # Event detection algorithm tests
│   │   ├── test_security_analyzer.py  # Security analysis tests
│   │   └── test_threat_levels.py      # Threat classification tests
│   ├── test_rtl_sdr/                  # RTL-SDR system tests
│   │   ├── test_signal_bridge.py      # Signal processing tests
│   │   └── test_rtl_tcp_server.py     # Server management tests
│   ├── test_hardware/                  # Hardware abstraction tests
│   │   ├── test_mock_devices.py       # Mock hardware tests
│   │   └── test_interfaces.py         # Hardware interface tests
│   └── integration/                    # End-to-end integration tests
│       ├── test_full_system.py        # Complete system integration
│       └── test_hardware_integration.py # Hardware integration tests
├── docs/                               # Comprehensive project documentation
│   ├── api/                           # API documentation and specifications
│   │   ├── detection_api.md           # Detection system API reference
│   │   └── hardware_api.md            # Hardware interface API reference
│   ├── diagrams/                      # Architecture and system diagrams
│   │   ├── system_architecture.mmd    # Mermaid system architecture diagram
│   │   ├── data_flow.mmd             # Data flow diagram
│   │   └── threat_detection_flow.mmd  # Threat detection process flow
│   ├── plans/                         # Project planning and roadmap documents
│   │   ├── development_roadmap.md     # Long-term development plan
│   │   ├── testing_strategy.md        # Comprehensive testing approach
│   │   └── deployment_guide.md        # Production deployment guide
│   ├── research/                      # Research papers and references
│   │   ├── automotive_security.md     # Automotive security research
│   │   ├── rf_analysis_techniques.md  # RF analysis methodologies
│   │   └── threat_modeling.md         # Security threat modeling
│   ├── detection_logic_explained.md   # Detailed detection algorithm explanation
│   ├── migration_plan.md              # System evolution and migration strategy
│   ├── poc_migration_plan.md          # POC to production migration guide
│   └── user_guide.md                  # End-user operation manual
├── rtl_sdr_bin/                       # RTL-SDR Windows binaries and drivers
│   ├── rtl_tcp.exe                    # RTL-TCP server executable
│   ├── rtl_test.exe                   # Hardware testing utility
│   ├── rtl_fm.exe                     # FM demodulation tool
│   └── drivers/                       # Windows USB drivers
├── scripts/                           # Development and deployment scripts
│   ├── setup_environment.py          # Automated environment setup
│   ├── run_tests.py                   # Test execution script
│   ├── deploy_pico.py                 # Pico W firmware deployment
│   └── generate_docs.py               # Documentation generation
├── config/                            # Configuration files and templates
│   ├── default_config.yaml           # Default system configuration
│   ├── development.yaml              # Development environment config
│   ├── production.yaml               # Production environment config
│   └── test.yaml                     # Testing environment config
├── logs/                              # Log file directory (created at runtime)
│   ├── detection_events.log          # Security event logs
│   ├── system.log                    # General system logs
│   └── hardware.log                  # Hardware interface logs
├── pyproject.toml                     # Modern Python project configuration (PEP 518)
├── requirements.txt                   # Python dependencies specification
├── requirements-dev.txt               # Development-only dependencies
├── pytest.ini                        # Pytest configuration and test markers
├── .env.example                       # Environment variable template
├── .gitignore                         # Git ignore patterns
├── setup.py                          # Legacy setup script (compatibility)
├── uv.lock                           # UV package manager lock file
└── README.md                         # Backend-specific documentation
```

## File Naming Conventions & Standards

### Python Code Standards
- **Snake_case**: All Python files, directories, functions, and variables
- **Descriptive Names**: Files clearly indicate their purpose and functionality
- **Module Organization**: Related functionality grouped in logical directories
- **Entry Points**: Main executable scripts at appropriate directory levels
- **Package Structure**: Proper `__init__.py` files for all packages

### Examples of Good Naming
```
# Good Examples
cli_dashboard.py              # Clear purpose: CLI dashboard
security_analyzer.py          # Clear purpose: security analysis
threat_levels.py             # Clear purpose: threat level definitions
mock_rtl_sdr.py              # Clear purpose: mock RTL-SDR implementation

# Avoid These Patterns
main.py                      # Too generic (except for Pico W entry point)
utils.py                     # Too broad (use specific utility modules)
helpers.py                   # Vague purpose
temp.py                      # Temporary files should not be committed
```

### Configuration File Standards
- **YAML**: Primary configuration format (human-readable, supports comments)
- **TOML**: Python project configuration (pyproject.toml)
- **INI**: Legacy configuration support (pytest.ini)
- **JSON**: API and data exchange formats
- **ENV**: Environment-specific variables

## Key Entry Points & System Interfaces

### Primary Entry Points
```python
# Main User Interface
backend/cli_dashboard.py
# Usage: python cli_dashboard.py [--mock|--source tcp|--source api]
# Purpose: Primary user interface for monitoring and demonstration

# System Orchestration
backend/rtl_sdr/startup_server.py
# Usage: python rtl_sdr/startup_server.py
# Purpose: Automated system startup and health monitoring

# Hardware Server
backend/rtl_sdr/rtl_tcp_server.py
# Usage: python rtl_sdr/rtl_tcp_server.py
# Purpose: RTL-SDR hardware server management

# Embedded Client
backend/pico/main.py
# Usage: Deployed to Raspberry Pi Pico W via Thonny or rshell
# Purpose: Hardware alert system and NFC interface
```

### System Integration Points
```python
# Detection System Integration
backend/cli_dashboard_detection_adapter.py
# Purpose: Bridge between UI and detection systems

# Signal Processing Bridge
backend/rtl_sdr/signal_bridge.py
# Purpose: Convert RF signals to security events

# Hardware Abstraction
backend/hardware/rtl_sdr_interface.py
backend/hardware/pico_interface.py
# Purpose: Clean hardware abstraction for testing and modularity
```

## Configuration Management Architecture

### Configuration File Hierarchy
```yaml
# config/default_config.yaml - Base configuration
system:
  name: "Automotive Security Monitor"
  version: "1.0.0"
  log_level: "INFO"

rtl_sdr:
  frequency: 433920000  # 433.92 MHz (key fobs, TPMS)
  sample_rate: 2048000  # 2.048 MS/s
  gain: "auto"
  tcp_port: 1234

detection:
  threat_threshold: 0.7
  analysis_window: 1.0  # seconds
  max_events_per_second: 100

pico:
  tcp_host: "192.168.1.100"
  tcp_port: 8888
  led_brightness: 128
  nfc_enabled: true
```

### Environment-Specific Overrides
```yaml
# config/development.yaml - Development overrides
system:
  log_level: "DEBUG"

rtl_sdr:
  mock_mode: true
  recording_path: "rtl_sdr/recordings/"

detection:
  threat_threshold: 0.5  # Lower threshold for testing
```

## Directory Purposes & Responsibilities

### Core System Directories

#### `/detection` - Security Analysis Engine
- **Purpose**: Core threat detection and security analysis logic
- **Key Components**:
  - Event detection algorithms and heuristics
  - Threat classification and scoring
  - Security report generation
  - Packet parsing and analysis
- **Design Pattern**: Strategy pattern for different detection algorithms
- **Testing**: Comprehensive unit tests with mock RF data

#### `/rtl_sdr` - Hardware Interface Layer
- **Purpose**: RTL-SDR hardware integration and signal processing
- **Key Components**:
  - Hardware server management and control
  - Real-time signal processing and FFT analysis
  - TCP server for signal distribution
  - System startup and orchestration
- **Design Pattern**: Adapter pattern for hardware abstraction
- **Performance**: Optimized for real-time signal processing

#### `/pico` - Embedded Alert System
- **Purpose**: Raspberry Pi Pico W firmware and hardware interfaces
- **Key Components**:
  - MicroPython TCP client for alert reception
  - LED control for visual threat indication
  - NFC/RFID interface for proximity interactions
  - Network configuration and management
- **Design Pattern**: Event-driven architecture for real-time alerts
- **Constraints**: Memory and processing limitations of embedded system

#### `/hardware` - Hardware Abstraction Layer
- **Purpose**: Clean abstraction layer for all hardware components
- **Key Components**:
  - RTL-SDR interface abstraction
  - Pico W communication interface
  - Mock implementations for testing
  - Hardware capability detection
- **Design Pattern**: Abstract factory pattern for hardware creation
- **Benefits**: Enables testing without physical hardware

### Support Directories

#### `/utils` - Shared Utilities
- **Purpose**: Common functionality used across multiple modules
- **Key Components**:
  - Logging configuration and management
  - Configuration file parsing and validation
  - Signal processing helper functions
  - Network communication utilities
- **Design Pattern**: Utility/helper pattern with static methods
- **Principle**: DRY (Don't Repeat Yourself) implementation

#### `/tests` - Comprehensive Test Suite
- **Purpose**: Ensure system reliability and correctness
- **Test Categories**:
  - Unit tests for individual components
  - Integration tests for system interactions
  - Hardware tests (require physical devices)
  - Performance tests for real-time requirements
- **Framework**: pytest with asyncio support and custom markers
- **Coverage**: Target >90% code coverage

#### `/docs` - Documentation Ecosystem
- **Purpose**: Comprehensive project documentation and knowledge base
- **Documentation Types**:
  - API documentation and specifications
  - Architecture diagrams and system design
  - Research papers and technical references
  - User guides and operation manuals
- **Format**: Markdown with Mermaid diagrams
- **Maintenance**: Documentation updated with code changes

#### `/scripts` - Automation and Deployment
- **Purpose**: Automate common development and deployment tasks
- **Script Categories**:
  - Environment setup and configuration
  - Testing and quality assurance
  - Deployment and distribution
  - Documentation generation
- **Language**: Python for consistency with main codebase
- **Integration**: Integrated with CI/CD pipelines

## Code Organization Principles & Patterns

### Architectural Patterns

#### Layered Architecture
```
┌─────────────────────────────────────┐
│           User Interface            │  cli_dashboard.py
├─────────────────────────────────────┤
│         Application Logic           │  detection/, adapters
├─────────────────────────────────────┤
│        Hardware Abstraction         │  hardware/
├─────────────────────────────────────┤
│         Physical Hardware           │  RTL-SDR, Pico W
└─────────────────────────────────────┘
```

#### Event-Driven Architecture
- **Event Sources**: RTL-SDR signal capture, network events
- **Event Processors**: Detection algorithms, threat analysis
- **Event Consumers**: CLI dashboard, Pico W alerts, log files
- **Benefits**: Loose coupling, scalability, real-time processing

#### Dependency Injection
- **Configuration Injection**: System settings injected at startup
- **Hardware Injection**: Hardware interfaces injected for testing
- **Service Injection**: Services injected for modularity
- **Benefits**: Testability, flexibility, maintainability

### Design Principles

#### Single Responsibility Principle (SRP)
- Each module has one clear, focused purpose
- Files are named to reflect their specific responsibility
- Classes and functions have single, well-defined roles

#### Open/Closed Principle (OCP)
- System open for extension (new detection algorithms)
- System closed for modification (stable interfaces)
- Plugin architecture for future enhancements

#### Dependency Inversion Principle (DIP)
- High-level modules don't depend on low-level modules
- Both depend on abstractions (interfaces)
- Hardware abstraction enables testing and flexibility

#### Don't Repeat Yourself (DRY)
- Common functionality extracted to utility modules
- Configuration centralized and reusable
- Code generation for repetitive patterns

### Testing Strategy & Organization

#### Test Categories (pytest markers)
```python
# Unit Tests - Fast, isolated, no external dependencies
@pytest.mark.unit
def test_threat_level_classification():
    pass

# Integration Tests - Test component interactions
@pytest.mark.integration
def test_detection_pipeline():
    pass

# Hardware Tests - Require physical hardware
@pytest.mark.hardware
def test_rtl_sdr_connection():
    pass

# Slow Tests - Long-running or resource-intensive
@pytest.mark.slow
def test_performance_under_load():
    pass
```

#### Mock Strategy
- **Hardware Mocking**: Complete mock implementations for all hardware
- **Network Mocking**: Mock TCP connections and HTTP requests
- **Time Mocking**: Control time for deterministic testing
- **Data Mocking**: Synthetic RF signals and events for testing

### Documentation Standards

#### Code Documentation
- **Docstrings**: Google-style docstrings for all public functions
- **Type Hints**: Comprehensive type annotations throughout
- **Comments**: Explain complex algorithms and business logic
- **Examples**: Usage examples in docstrings

#### Architecture Documentation
- **Mermaid Diagrams**: System architecture and data flow
- **API Documentation**: Comprehensive API reference
- **Decision Records**: Document architectural decisions and rationale
- **User Guides**: Step-by-step operation instructions

This comprehensive structure ensures maintainability, testability, and scalability while supporting the educational goals of the capstone project.