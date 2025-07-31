# Environment Setup Guide for Final Report

This section provides a comprehensive, single-source-of-truth guide for setting up the development and runtime environment for the automotive security monitoring system.

## System Requirements

### Hardware Requirements

| Component | Minimum | Recommended | Purpose |
|-----------|---------|-------------|---------|
| **CPU** | Intel i5 / AMD Ryzen 5 | Intel i7 / AMD Ryzen 7 | Signal processing |
| **RAM** | 8GB | 16GB | Real-time analysis |
| **Storage** | 10GB free space | SSD with 20GB | Performance |
| **USB** | USB 2.0 | USB 3.0 | RTL-SDR connection |
| **Network** | WiFi 802.11n | WiFi 802.11ac | Pico W communication |

### Software Requirements

| Software | Version | Platform | Purpose |
|----------|---------|----------|---------|
| **Python** | 3.11+ | Windows/Linux/macOS | Core runtime |
| **UV** | Latest | All platforms | Package management (recommended) |
| **RTL-SDR Tools** | Latest | Windows/Linux | Hardware drivers |
| **Git** | 2.30+ | All platforms | Version control |

## Operating System Setup

### Windows Setup

#### 1. Python Installation
```powershell
# Download Python 3.11+ from python.org
# Ensure "Add Python to PATH" is checked during installation

# Verify installation
python --version
pip --version
```

#### 2. RTL-SDR Drivers
```powershell
# RTL-SDR tools are included in backend/rtl_sdr_bin/
# For driver installation:
# 1. Download Zadig from zadig.akeo.ie
# 2. Connect RTL-SDR device
# 3. Run Zadig as administrator
# 4. Select RTL-SDR device
# 5. Install WinUSB driver

# Verify RTL-SDR installation
cd backend/rtl_sdr_bin
rtl_test.exe
```

#### 3. UV Package Manager (Recommended)
```powershell
# Install UV for faster package management
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

### Linux Setup (Ubuntu/Debian)

#### 1. System Dependencies
```bash
# Update package list
sudo apt-get update

# Install Python and development tools
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
sudo apt-get install -y build-essential git curl

# Install RTL-SDR tools and libraries
sudo apt-get install -y rtl-sdr librtlsdr-dev

# Verify RTL-SDR installation
rtl_test
```

#### 2. UV Package Manager (Recommended)
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (add to ~/.bashrc for persistence)
export PATH="$HOME/.cargo/bin:$PATH"

# Verify installation
uv --version
```

#### 3. USB Permissions (Linux)
```bash
# Add user to plugdev group for RTL-SDR access
sudo usermod -a -G plugdev $USER

# Create udev rule for RTL-SDR devices
sudo tee /etc/udev/rules.d/20-rtlsdr.rules > /dev/null <<EOF
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", GROUP="plugdev", MODE="0666", SYMLINK+="rtl_sdr"
EOF

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Log out and back in for group changes to take effect
```

### macOS Setup

#### 1. Homebrew and Dependencies
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and RTL-SDR tools
brew install python@3.11 rtl-sdr

# Verify installations
python3.11 --version
rtl_test
```

#### 2. UV Package Manager
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

## Project Environment Setup

### 1. Repository Clone and Navigation

```bash
# Clone the repository
git clone <repository-url>
cd automotive-security-capstone

# Navigate to backend directory
cd backend
```

### 2. Python Virtual Environment

#### Using UV (Recommended)
```bash
# Create virtual environment with UV
uv venv

# Activate virtual environment
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Install development dependencies (for testing)
uv pip install -r requirements-dev.txt
```

#### Using Standard pip (Alternative)
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (for testing)
pip install -r requirements-dev.txt
```

### 3. Environment Verification

```bash
# Verify Python environment
python --version
pip list

# Test core imports
python -c "import numpy, scipy, rich, asyncio; print('Core dependencies OK')"

# Test RTL-SDR hardware detection (if hardware connected)
python -c "from hardware.rtl_sdr_interface import RTLSDRInterface; rtl = RTLSDRInterface(); print('RTL-SDR interface OK')"
```

## Hardware Setup

### RTL-SDR V4 Setup

#### 1. Hardware Connection
```bash
# Connect RTL-SDR V4 to USB 3.0 port (recommended)
# Use included antenna or external antenna for better reception

# Test hardware detection
rtl_test

# Expected output should show device information
# Example: "Found 1 device(s): 0: Realtek, RTL2838UHIDIR, SN: 00000001"
```

#### 2. Driver Verification
```bash
# Test RTL-SDR functionality
rtl_test -t

# Test frequency scanning (optional)
rtl_power -f 300M:450M:1M -i 10

# Test TCP server functionality
rtl_tcp -a 127.0.0.1 -p 1234
# Should show: "listening on 127.0.0.1:1234"
# Press Ctrl+C to stop
```

### Raspberry Pi Pico W Setup

#### 1. MicroPython Firmware Installation

```bash
# 1. Download MicroPython firmware for Pico W
# Visit: https://micropython.org/download/rp2-pico-w/
# Download the latest .uf2 file

# 2. Flash firmware to Pico W
# - Hold BOOTSEL button while connecting USB cable
# - Pico W appears as USB drive (RPI-RP2)
# - Copy .uf2 file to the drive
# - Pico W will reboot with MicroPython
```

#### 2. Automated Code Deployment

```bash
# Deploy Pico W code automatically
uv run python deploy_pico.py

# Manual port specification if auto-detection fails
# Windows
uv run python deploy_pico.py COM3

# Linux
uv run python deploy_pico.py /dev/ttyACM0

# macOS
uv run python deploy_pico.py /dev/cu.usbmodem*
```

#### 3. Network Configuration

Edit `backend/pico/config.py`:

```python
# WiFi Configuration
WIFI_SSID = "your_network_name"
WIFI_PASSWORD = "your_wifi_password"

# TCP Server Configuration (your computer's IP)
TCP_HOST = "192.168.1.100"  # Replace with your computer's IP
TCP_PORT = 8888

# Hardware Configuration
LED_PIN_RED = 15      # GPIO pin for red LED
LED_PIN_YELLOW = 14   # GPIO pin for yellow LED  
LED_PIN_GREEN = 13    # GPIO pin for green LED

# NFC Configuration (if using PN532 module)
NFC_ENABLED = True
NFC_SDA_PIN = 4       # I2C SDA pin
NFC_SCL_PIN = 5       # I2C SCL pin
```

## Network Configuration

### 1. Find Computer IP Address

```bash
# Windows
ipconfig

# Linux
ip addr show
# or
hostname -I

# macOS
ifconfig
```

### 2. Firewall Configuration

#### Windows Firewall
```powershell
# Allow TCP port 8888 for event server
netsh advfirewall firewall add rule name="Automotive Security Event Server" dir=in action=allow protocol=TCP localport=8888

# Verify rule
netsh advfirewall firewall show rule name="Automotive Security Event Server"
```

#### Linux Firewall (UFW)
```bash
# Allow TCP port 8888
sudo ufw allow 8888/tcp

# Check status
sudo ufw status
```

#### macOS Firewall
```bash
# macOS firewall typically allows outgoing connections by default
# If issues occur, check System Preferences > Security & Privacy > Firewall
```

## Development Tools Setup

### 1. Code Editor Configuration

#### VS Code (Recommended)
```bash
# Install VS Code extensions
code --install-extension ms-python.python
code --install-extension ms-python.pylint
code --install-extension ms-python.black-formatter
code --install-extension charliermarsh.ruff

# Open project
code .
```

#### PyCharm
```bash
# Configure Python interpreter to use virtual environment
# File > Settings > Project > Python Interpreter
# Select .venv/bin/python (Linux/macOS) or .venv\Scripts\python.exe (Windows)
```

### 2. Git Configuration

```bash
# Configure Git (if not already done)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify configuration
git config --list
```

## Environment Testing

### 1. Quick System Test

```bash
# Test demo mode (no hardware required)
uv run python cli_dashboard.py --mock

# Expected: CLI dashboard with simulated automotive security events
# Press 'q' to quit
```

### 2. Hardware Integration Test

```bash
# Test RTL-SDR detection
uv run python -c "
from hardware.rtl_sdr_interface import RTLSDRInterface
rtl = RTLSDRInterface()
devices = rtl.detect_hardware()
print(f'Detected {len(devices)} RTL-SDR device(s)')
for device in devices:
    print(f'  - {device}')
"

# Test complete system with hardware
uv run python real_hardware_launcher.py

# Expected: System starts with hardware detection and status reporting
```

### 3. Pico W Connection Test

```bash
# Check Pico W serial connection
# Windows
python -c "import serial.tools.list_ports; print([port.device for port in serial.tools.list_ports.comports()])"

# Linux/macOS  
python -c "import serial.tools.list_ports; print([port.device for port in serial.tools.list_ports.comports()])"

# Test Pico W deployment
uv run python deploy_pico.py --test-connection
```

## Performance Optimization

### 1. System Performance Settings

#### Windows
```powershell
# Set high performance power plan
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

# Disable USB selective suspend
# Control Panel > Power Options > Change plan settings > Change advanced power settings
# USB settings > USB selective suspend setting > Disabled
```

#### Linux
```bash
# Install performance tools
sudo apt-get install -y cpufrequtils

# Set CPU governor to performance
sudo cpufreq-set -g performance

# Disable USB autosuspend for RTL-SDR
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", ATTR{power/autosuspend}="-1"' | sudo tee -a /etc/udev/rules.d/20-rtlsdr.rules
```

### 2. Python Performance

```bash
# Verify NumPy is using optimized BLAS
python -c "import numpy; numpy.show_config()"

# Install optimized NumPy if needed (Intel MKL)
# This is typically handled automatically by modern pip/conda
```

## Troubleshooting Common Issues

### 1. Python Environment Issues

```bash
# Clear pip cache
pip cache purge

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Check for conflicting packages
pip check
```

### 2. RTL-SDR Issues

```bash
# Test RTL-SDR with verbose output
rtl_test -t

# Check USB connection
lsusb | grep RTL  # Linux
# or check Device Manager on Windows

# Reset RTL-SDR device
sudo rmmod dvb_usb_rtl28xxu rtl2832 rtl2830  # Linux
sudo modprobe dvb_usb_rtl28xxu
```

### 3. Network Connectivity Issues

```bash
# Test network connectivity
ping 192.168.1.1  # Replace with your router IP

# Check port availability
netstat -an | grep 8888

# Test TCP connection
telnet localhost 8888
```

## Environment Variables

### Optional Configuration

Create `.env` file in backend directory:

```bash
# RTL-SDR Configuration
RTL_SDR_DEVICE=0
RTL_SDR_FREQUENCY=433920000
RTL_SDR_SAMPLE_RATE=2048000
RTL_SDR_GAIN=auto

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/system.log

# Development Settings
DEBUG_MODE=false
MOCK_MODE=false

# Network Configuration
TCP_HOST=localhost
TCP_PORT=8888
```

## Validation

### Final Environment Check

```bash
# Run comprehensive environment validation
uv run python -c "
import sys
print(f'Python version: {sys.version}')

# Test core dependencies
try:
    import numpy, scipy, rich, asyncio, serial, aiohttp
    print('✅ Core dependencies: OK')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')

# Test hardware interfaces
try:
    from hardware.rtl_sdr_interface import RTLSDRInterface
    from hardware.pico_connection_manager import PicoConnectionManager
    print('✅ Hardware interfaces: OK')
except ImportError as e:
    print(f'❌ Hardware interface error: {e}')

# Test detection modules
try:
    from detection.security_analyzer import SecurityAnalyzer
    from rtl_sdr.automotive_signal_analyzer import AutomotiveSignalAnalyzer
    print('✅ Detection modules: OK')
except ImportError as e:
    print(f'❌ Detection module error: {e}')

print('Environment setup complete!')
"
```

This comprehensive environment setup guide ensures all dependencies and configurations are properly installed and configured for the automotive security monitoring system.