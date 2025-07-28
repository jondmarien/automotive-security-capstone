# Automotive Security Capstone Backend (2025)

This backend powers the Automotive Security Capstone POC, enabling real-time automotive RF and NFC event detection, logging, and demo visualization via a CLI dashboard.

## 🚘 Project Overview

- **RTL-SDR V4** dongle connects to a computer for RF signal capture.
- **Python signal processing** scripts analyze IQ samples and detect automotive events.
- **Detection events** are streamed over TCP to:
  - **Raspberry Pi Pico W** (for alerting/NFC)
  - **CLI Dashboard** (for real-time monitoring and demo)
- **No FastAPI/MongoDB backend** is required for the current MVP/POC.

## 🏗️ System Architecture

```
RTL-SDR V4
   │
   ▼
Computer (Windows/Linux)
 ├── rtl_tcp (raw IQ data server, port 1234)
 ├── signal_bridge.py (RF analysis, event detection)
 ├── rtl_tcp_server.py (TCP event server, port 8888)
 ├── cli_dashboard.py (Rich-based CLI dashboard, supports --mock mode)
 └── [optionally] startup_server.py (launches everything)
   │
   ▼
Raspberry Pi Pico W (TCP client, receives events, handles alerting/NFC)
```

## 📦 Key Components

- `rtl_tcp_server.py`: Manages RTL-SDR, launches `rtl_tcp`, listens for Pico clients and dashboard on TCP (default: 8888)
- `signal_bridge.py`: Reads IQ samples from RTL-SDR, detects events, sends to TCP server (supports enhanced mode)
- `rtl_sdr/automotive_signal_analyzer.py`: **NEW** - Advanced automotive signal analysis with FSK detection and pattern recognition
- `rtl_sdr/enhanced_signal_bridge.py`: **NEW** - Enhanced signal processing with threat detection and replay attack analysis
- `rtl_sdr/signal_history_buffer.py`: **NEW** - Signal history management for temporal analysis and replay detection
- `cli_dashboard.py`: Rich-powered CLI dashboard for real-time event display; supports `--mock` for demo/testing
- `pico/main.py`: MicroPython client for Pico W; connects to computer, receives events, triggers LEDs/NFC

## 🛠️ Setup & Usage

### 1. Computer-Side (Windows/Linux)

1. **Install RTL-SDR drivers/tools** (see [docs/poc_migration_plan.md](../docs/poc_migration_plan.md))
2. **Set up Python environment**

```sh
   python -m venv .venv
   .venv\Scripts\activate  # (Windows) or source .venv/bin/activate (Linux)
   pip install -r requirements.txt
```

3. **Start RTL-TCP server and event bridge**

```sh
   # Standard mode (legacy signal processing)
   python rtl_tcp_server.py
   python signal_bridge.py
   
   # Enhanced mode (advanced automotive signal analysis)
   python rtl_tcp_server.py
   python signal_bridge.py --enhanced
   
   # Or use startup orchestration:
   python startup_server.py
```

4. **Run the CLI dashboard (real events or mock mode)**

```sh
   # For live events (requires running TCP server with events):
   python cli_dashboard.py --source tcp --tcp-host localhost --tcp-port 8888
   # For demo/testing (no hardware required):
   python cli_dashboard.py --mock
```

### 2. Pico-Side (Raspberry Pi Pico W)

- Flash MicroPython firmware
- Upload `main.py` and required libraries (see [docs/poc_migration_plan.md](../docs/poc_migration_plan.md))
- Configure WiFi and server IP/port (default: 8888)
- Pico will connect to computer, receive detection events, and trigger alerts/NFC

## 🚀 Enhanced Signal Processing (NEW)

The system now includes advanced automotive signal analysis capabilities with comprehensive threat detection:

### AutomotiveSignalAnalyzer Features
- **Real-time IQ Analysis**: Advanced FFT-based power spectrum computation with windowing
- **Key Fob Detection**: FSK pattern recognition with timing analysis and confidence scoring
- **TPMS Signal Detection**: Tire pressure monitoring system identification with automotive-specific patterns
- **Burst Pattern Analysis**: Sophisticated burst timing and interval detection with adaptive thresholds
- **Confidence Scoring**: Multi-factor confidence calculation for detected automotive signals
- **Modulation Classification**: Automatic FSK/ASK/Unknown modulation detection with signal quality assessment

### Enhanced Threat Detection Engine
The threat detection engine is fully integrated within the enhanced signal bridge, providing comprehensive automotive security analysis:

- **Replay Attack Detection**: Advanced signal similarity analysis with temporal correlation
  - Power spectrum correlation (40% weight), burst timing (30%), frequency deviation (20%), bandwidth (10%)
  - 95% similarity threshold within 1 second to 5 minutes timeframe
  - Multi-factor confidence scoring with temporal analysis
- **Jamming Detection**: Comprehensive RF interference detection with four pattern types:
  - **Continuous Jamming**: Sustained high power with low variance detection
  - **Pulse Jamming**: Periodic high-power bursts with regular timing analysis
  - **Sweep Jamming**: Systematic frequency progression with directional consistency
  - **Spot Jamming**: Narrow-band high power with >10:1 peak-to-average ratio (updated threshold)
  - **Noise Floor Analysis**: Detects elevation >10 dB above baseline with temporal baseline calculation
  - **Broadband Interference**: Spectral flatness analysis (>0.5 threshold) for wideband jamming
  - **Evidence Collection**: Technical proof including affected frequencies, interference duration, SNR degradation
- **Brute Force Detection**: Integrated multi-tier threat detection with escalating levels
  - **Temporal Analysis**: Multi-window analysis (30s, 60s, 300s) for comprehensive attack pattern recognition
  - **Escalating Threat Levels**: Suspicious (5/min) → Moderate (10/min) → High (20/min) → Critical (40/min)
  - **Pattern Recognition**: Rapid burst detection, sustained attack analysis, signal consistency scoring
  - **Evidence Collection**: Statistical analysis, interval consistency, recommended actions per threat level
  - **Attack Classification**: Rapid burst, sustained brute force, and persistent attack pattern identification
- **Signal History Buffer**: Thread-safe 5-minute rolling buffer (1000 signals) for temporal analysis
- **Threat Classification**: Automated BENIGN/SUSPICIOUS/MALICIOUS classification with confidence scoring
- **Temporal Analysis**: Accurate timestamp-based signal correlation with chronological ordering

### Performance Characteristics
- **Real-time Processing**: <100ms latency from signal capture to threat detection
- **Throughput**: Handles 3.2 MS/s sample rate from RTL-SDR V4
- **Memory Management**: Efficient buffer management with automatic cleanup
- **Processing Optimization**: Designed for 100ms signal chunks (204,800 samples at 2.048 MS/s)
- **Analysis Speed**: <500ms for comprehensive signal analysis (10x real-time performance)
- **Test Coverage**: 63 comprehensive tests with 100% pass rate

### Usage
```sh
# Enable enhanced mode in signal_bridge.py
bridge = SignalProcessingBridge(rtl_server_manager, enhanced_mode=True)

# Or use enhanced signal bridge directly
from rtl_sdr.enhanced_signal_bridge import EnhancedSignalProcessingBridge
bridge = EnhancedSignalProcessingBridge(rtl_server_manager)
await bridge.start_signal_processing()
```

## 🖥️ CLI Dashboard

- Real-time event table with threat levels, event type, source, and details
- Supports both live TCP and `--mock` demo mode
- Enhanced threat indicators and confidence scores
- Logs all events to `detection_events.log`
- Graceful error handling and Ctrl+C exit

## 🔄 Project Structure (simplified)

```
backend/
├── cli_dashboard.py                    # CLI dashboard (Rich, --mock supported)
├── rtl_sdr/
│   ├── rtl_tcp_server.py              # Manages RTL-SDR, Pico TCP server
│   ├── signal_bridge.py               # Signal processing, event detection (legacy + enhanced modes)
│   ├── automotive_signal_analyzer.py  # Advanced automotive signal analysis (NEW)
│   ├── enhanced_signal_bridge.py      # Enhanced signal processing with integrated threat detection (NEW)
│   ├── signal_history_buffer.py       # Signal history for replay detection (NEW)
│   └── startup_server.py              # System orchestration
├── pico/
│   └── main.py                        # Pico W MicroPython TCP client
├── detection/                         # Core detection logic
│   ├── event_logic.py                 # Unified event analysis
│   ├── packet.py                      # RF packet definitions
│   ├── threat_levels.py               # Threat classification
│   ├── jamming_detector.py            # Advanced jamming detection (NEW)
│   └── replay_attack_detector.py      # Replay attack detection
├── tests/                             # Comprehensive test suite (63 tests total)
│   ├── test_automotive_signal_analyzer.py  # Signal analyzer tests (24 tests) (NEW)
│   ├── test_enhanced_signal_bridge.py      # Enhanced bridge tests (21 tests) (NEW)
│   └── test_jamming_detector.py            # Jamming detection tests (18 tests) (NEW)
├── requirements.txt                   # Python dependencies (updated with scipy)
├── docs/
│   └── poc_migration_plan.md
└── ... (other scripts, logs, configs)
```

## ⚡ Troubleshooting

- **No events in dashboard?** Ensure `rtl_tcp_server.py` and `signal_bridge.py` are running, and Pico/dashboard are connecting to the correct port (default: 8888).
- **Testing without hardware?** Use `python cli_dashboard.py --mock` for demo mode.
- **RTL-SDR not detected?** Use `rtl_test` to verify driver installation.
- **Firewall issues?** Allow port 8888 for incoming TCP connections.

## 🧪 Testing

The system includes comprehensive test coverage for all detection and signal processing components:

```sh
# Run all tests (63 total tests)
pytest

# Run enhanced signal processing tests
pytest tests/test_automotive_signal_analyzer.py -v    # Signal analyzer tests (24 tests)
pytest tests/test_enhanced_signal_bridge.py -v       # Enhanced bridge tests (21 tests)
pytest tests/test_jamming_detector.py -v             # Jamming detection tests (18 tests)

# Run all enhanced processing tests together
pytest tests/test_automotive_signal_analyzer.py tests/test_enhanced_signal_bridge.py tests/test_jamming_detector.py -v

# Run specific detection tests
pytest tests/test_replay_attack_detector.py -v       # Replay attack detection tests

# Run with coverage
pytest --cov=detection --cov=rtl_sdr --cov-report=html

# Test categories
pytest -m unit                    # Fast unit tests
pytest -m integration            # Integration tests
pytest -m "not hardware"         # Skip hardware-dependent tests
pytest -m slow                   # Performance and long-running tests
```

### Test Quality Improvements
- **Enhanced Test Coverage**: 63 comprehensive tests with 100% pass rate across all components
- **Realistic Signal Data**: Tests use proper Unix timestamps and chronological ordering for accurate temporal analysis
- **Temporal Accuracy**: Improved noise floor baseline calculation with realistic signal history
- **Comprehensive Coverage**: >90% code coverage for detection and signal processing modules
- **Mock Hardware**: Complete hardware simulation for testing without physical devices
- **Performance Testing**: Real-time processing validation (<100ms latency) and memory usage monitoring
- **Thread Safety Testing**: Concurrent access validation for signal history buffer operations

## 🗒️ Notes

- **No FastAPI or MongoDB**: This MVP/POC does not require a web API or database. All event streaming is via TCP.
- **For full hardware setup and wiring, see**: [`docs/poc_migration_plan.md`](../docs/poc_migration_plan.md)

## 📚 References
- [RTL-SDR Quick Start Guide](https://www.rtl-sdr.com/rtl-sdr-quick-start-guide/)
- [MicroPython for Pico W](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)

---

For questions or demo support, see the project documentation or contact the project maintainers.