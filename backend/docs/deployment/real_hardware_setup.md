# Real Hardware Setup Guide

## Overview

This guide covers the complete setup and deployment of the automotive security monitoring system with real RTL-SDR V4 and Raspberry Pi Pico W hardware. The system now includes comprehensive hardware management with automatic detection, failure recovery, and graceful fallback to mock mode.

## Hardware Requirements

### RTL-SDR V4 Dongle
- **Model**: RTL-SDR Blog V4 (R828D tuner + RTL2832U)
- **Frequency Range**: 500 kHz - 1.75 GHz (covers automotive frequencies)
- **Sample Rate**: Up to 3.2 MS/s (configurable)
- **Interface**: USB 3.0 for high-speed data transfer
- **Driver**: librtlsdr with Python bindings
- **Cost**: ~$30 USD

### Raspberry Pi Pico W
- **MCU**: RP2040 dual-core ARM Cortex-M0+ @ 133MHz
- **Wireless**: 802.11n WiFi (2.4GHz band)
- **GPIO**: 26 programmable pins for LEDs, sensors, displays
- **Programming**: MicroPython for rapid development
- **Power**: USB or external 5V supply
- **Cost**: ~$6 USD

### PN532 NFC Module (Optional)
- **Interface**: SPI connection to Pico W
- **Frequency**: 13.56 MHz NFC/RFID
- **Range**: ~5-7cm for proximity detection
- **Standards**: ISO/IEC 14443A/MIFARE, FeliCa, ISO/IEC 14443B
- **Cost**: ~$8 USD

## System Architecture

```
┌─────────────────┐    USB 3.0     ┌─────────────────┐
│   RTL-SDR V4    │◄──────────────►│  Computer       │
│   (RF Capture)  │                │  (Processing)   │
└─────────────────┘                │                 │
                                   │ Hardware Mgr    │
                                   │ Recovery System │
                                   │ Logging System  │
                                   └─────────────────┘
                                           │
                                           │ WiFi/TCP
                                           ▼
                                   ┌─────────────────┐
                                   │ Raspberry Pi    │
                                   │ Pico W          │
                                   │ (Alerts/NFC)    │
                                   └─────────────────┘
```

## Software Installation

### Computer Setup (Windows/Linux)

#### 1. RTL-SDR Drivers and Tools

**Windows:**
```bash
# Download RTL-SDR drivers from rtl-sdr.com
# Install Zadig for USB driver management
# RTL-SDR tools are included in backend/rtl_sdr_bin/
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install rtl-sdr librtlsdr-dev

# Verify installation
rtl_test
```

#### 2. Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux

# Install dependencies
pip install -r requirements.txt

# Or use UV (recommended)
uv venv
uv pip install -r requirements.txt
```

#### 3. Hardware Detection Test

```bash
# Test RTL-SDR detection
rtl_test

# Test Python hardware interface
uv run python -c "from hardware.rtl_sdr_interface import RTLSDRInterface; rtl = RTLSDRInterface(); print('Detected:', rtl.detect_hardware())"
```

### Pico W Setup

#### 1. MicroPython Firmware Installation

```bash
# 1. Download latest MicroPython firmware for Pico W
wget https://micropython.org/download/rp2-pico-w/rp2-pico-w-latest.uf2

# 2. Flash firmware
# Hold BOOTSEL button while connecting USB
# Copy firmware file to RPI-RP2 drive
cp rp2-pico-w-latest.uf2 /media/RPI-RP2/
```

#### 2. Automated Code Deployment

```bash
# Automatic deployment with port detection
uv run python deploy_pico.py

# Manual port specification
uv run python deploy_pico.py COM3      # Windows
uv run python deploy_pico.py /dev/ttyACM0  # Linux
```

#### 3. Manual Code Deployment (Alternative)

```bash
# Using Thonny IDE
# 1. Install Thonny IDE
# 2. Connect to Pico W
# 3. Upload files: main.py, config.py, NFC_PN532.py

# Using rshell
pip install rshell
rshell -p COM3
> cp backend/pico/main.py /pyboard/
> cp backend/pico/config.py /pyboard/
> cp backend/pico/NFC_PN532.py /pyboard/
```

## Configuration

### Network Configuration

#### 1. Pico W WiFi Setup

Edit `backend/pico/config.py`:

```python
# Network Configuration
WIFI_SSID = "your_network_name"
WIFI_PASSWORD = "your_wifi_password"

# TCP Server Configuration
TCP_HOST = "192.168.1.100"  # Your computer's IP address
TCP_PORT = 8888             # Event server port
```

#### 2. Computer Network Setup

```bash
# Find your computer's IP address
# Windows
ipconfig

# Linux
ip addr show

# Update Pico config with this IP address
```

### Hardware Configuration

#### 1. RTL-SDR Configuration

The system automatically detects and configures RTL-SDR hardware:

```python
# Automatic configuration for automotive monitoring
# - Frequency: 433.92 MHz (European) or 315 MHz (North American)
# - Sample Rate: 2.048 MS/s (optimal for key fob monitoring)
# - Gain: Auto (optimized for signal reception)
```

#### 2. Frequency Band Selection

```bash
# European key fobs (433.92 MHz) - Default
uv run python real_hardware_launcher.py

# North American key fobs (315 MHz)
uv run python real_hardware_launcher.py --frequency 315000000

# Custom frequency
uv run python real_hardware_launcher.py --frequency 868000000
```

## System Launch

### Quick Demo Launch (Recommended for Presentations)

```bash
# Navigate to backend directory
cd backend

# Basic demo with realistic automotive security events (RECOMMENDED)
uv run python cli_dashboard.py --mock

# Advanced demo with synthetic signal generation
uv run python cli_dashboard.py --mock --synthetic

# View specific event for detailed analysis
uv run python cli_dashboard.py --mock --event 3
```

### Complete System Launch (Real Hardware)

```bash
# Launch with automatic hardware detection
uv run python real_hardware_launcher.py

# Force demo mode for presentations (system-wide)
uv run python real_hardware_launcher.py --force-mock

# Custom frequency configuration
uv run python real_hardware_launcher.py --frequency 315000000
```

### Manual Launch (Legacy)

```bash
# Terminal 1: Start RTL-SDR server
uv run python rtl_sdr/rtl_tcp_server.py

# Terminal 2: Start signal processing
uv run python rtl_sdr/signal_bridge.py --enhanced

# Terminal 3: Start CLI dashboard
uv run python cli_dashboard.py --source tcp --tcp-host localhost --tcp-port 8888
```

## Hardware Management Features

### Automatic Hardware Detection

The system automatically detects and configures hardware:

```python
# Hardware detection process
1. RTL-SDR Detection: Uses rtl_test to detect connected devices
2. Capability Assessment: Determines frequency range and supported features
3. Automotive Configuration: Optimizes settings for key fob monitoring
4. Health Monitoring: Continuous hardware health checks
5. Failure Recovery: Automatic recovery with exponential backoff
6. Mock Fallback: Graceful fallback to demo mode if hardware fails
```

### Hardware Status Monitoring

```bash
# System provides comprehensive status reporting:
# - RTL-SDR device name, tuner type, frequency range
# - Pico W connection count and health status
# - System uptime and performance metrics
# - Hardware failure detection and recovery attempts
```

### Recovery System

The system includes automatic hardware failure recovery:

```python
# Recovery features:
- Exponential backoff retry logic
- Maximum attempt limiting (5 attempts)
- Graceful degradation for partial failures
- Automatic fallback to mock mode
- Health monitoring with 15-second intervals
- Recovery attempt tracking and logging
```

## Deployment Verification

### 1. Hardware Detection Verification

```bash
# Run hardware detection test
uv run python -c "
from hardware import HardwareManager
import asyncio

async def test():
    manager = HardwareManager()
    success = await manager.initialize()
    health = manager.get_health_status()
    print(f'System Status: {health.system_status.value}')
    print(f'RTL-SDR: {health.rtl_sdr_status.value}')
    print(f'Pico W: {health.pico_connections}/{health.total_pico_devices}')

asyncio.run(test())
"
```

### 2. Pico W Connection Test

```bash
# Check Pico W connection logs
# Look for WiFi connection and TCP client messages
# Verify heartbeat messages are being received
```

### 3. End-to-End System Test

```bash
# Quick Demo Test (RECOMMENDED for initial verification)
uv run python cli_dashboard.py --mock

# Advanced Demo Test with synthetic signals
uv run python cli_dashboard.py --mock --synthetic

# Full System Test with Real Hardware
# 1. Launch system
uv run python real_hardware_launcher.py

# 2. Start dashboard in another terminal
uv run python cli_dashboard.py --source tcp

# 3. Verify events appear in dashboard
# 4. Check Pico W LED responses
```

## Performance Optimization

### RTL-SDR Optimization

```python
# Optimal settings for automotive monitoring:
FREQUENCY = 433920000      # 433.92 MHz (EU) or 315000000 (US)
SAMPLE_RATE = 2048000      # 2.048 MS/s
GAIN = "auto"              # Automatic gain control
BUFFER_SIZE = 262144       # 256KB buffer
```

### System Performance Targets

```python
# Performance requirements:
- Hardware Detection: <5 seconds
- Signal Processing: <100ms latency
- Event Generation: <50ms from detection to TCP
- Recovery Time: <30 seconds with exponential backoff
- Memory Usage: <100MB for complete system
- CPU Usage: <25% on modern hardware
```

### Network Optimization

```python
# Network configuration for optimal performance:
TCP_BUFFER_SIZE = 65536    # 64KB TCP buffer
HEARTBEAT_INTERVAL = 30    # 30-second heartbeat
CONNECTION_TIMEOUT = 10    # 10-second connection timeout
RETRY_ATTEMPTS = 5         # Maximum retry attempts
```

## Troubleshooting

### RTL-SDR Issues

**Problem**: RTL-SDR not detected
```bash
# Solutions:
1. Check USB connection (use USB 3.0 port if available)
2. Verify driver installation: rtl_test
3. Check device permissions (Linux): sudo usermod -a -G plugdev $USER
4. Try different USB port
5. Use --force-mock for demo mode
```

**Problem**: Poor signal reception
```bash
# Solutions:
1. Check antenna connection
2. Adjust gain settings
3. Move away from interference sources
4. Use external antenna for better reception
5. Check frequency configuration
```

### Pico W Issues

**Problem**: Pico W won't connect to WiFi
```bash
# Solutions:
1. Verify WiFi credentials in config.py
2. Check WiFi network (2.4GHz required)
3. Ensure network allows device connections
4. Check signal strength
5. Restart Pico W
```

**Problem**: TCP connection failures
```bash
# Solutions:
1. Verify computer IP address in config.py
2. Check firewall settings (allow port 8888)
3. Ensure computer and Pico on same network
4. Check TCP server is running
5. Verify port availability
```

### System Issues

**Problem**: Hardware recovery failures
```bash
# Solutions:
1. Check hardware connections
2. Restart system components
3. Review recovery logs
4. Use mock mode for testing
5. Check system resources (CPU, memory)
```

**Problem**: Performance issues
```bash
# Solutions:
1. Close unnecessary applications
2. Check system resources
3. Reduce sample rate if needed
4. Optimize buffer sizes
5. Use SSD for better I/O performance
```

## Logging and Diagnostics

### Log File Locations

```bash
# System logs are organized by date:
logs/
├── dashboard-2025-07-31/
│   ├── dashboard-09-30-15.log
│   └── dashboard-10-45-22.log
├── real_hardware_system.log
└── validation_20250731_123456/
    ├── accuracy_results.md
    └── confusion_matrix.png
```

### Diagnostic Commands

```bash
# Get comprehensive system diagnostics
uv run python -c "
from hardware import HardwareManager
import asyncio
import json

async def diagnostics():
    manager = HardwareManager()
    await manager.initialize()
    diag = manager.get_diagnostic_info()
    print(json.dumps(diag, indent=2))

asyncio.run(diagnostics())
"
```

### Health Monitoring

```bash
# Monitor system health in real-time
uv run python -c "
from hardware import HardwareManager
import asyncio

async def monitor():
    manager = HardwareManager()
    await manager.initialize()
    await manager.start_monitoring()
    
    while True:
        health = manager.get_health_status()
        print(f'Status: {health.system_status.value}, Uptime: {health.uptime:.1f}s')
        await asyncio.sleep(30)

asyncio.run(monitor())
"
```

## Production Deployment

### System Service Setup (Linux)

```bash
# Create systemd service
sudo nano /etc/systemd/system/automotive-security.service

[Unit]
Description=Automotive Security Monitoring System
After=network.target

[Service]
Type=simple
User=automotive
WorkingDirectory=/opt/automotive-security/backend
ExecStart=/opt/automotive-security/.venv/bin/python real_hardware_launcher.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Enable and start service
sudo systemctl enable automotive-security
sudo systemctl start automotive-security
```

### Windows Service Setup

```bash
# Use NSSM (Non-Sucking Service Manager)
nssm install "Automotive Security" "C:\automotive-security\.venv\Scripts\python.exe"
nssm set "Automotive Security" AppParameters "real_hardware_launcher.py"
nssm set "Automotive Security" AppDirectory "C:\automotive-security\backend"
nssm start "Automotive Security"
```

### Monitoring and Alerting

```bash
# Set up monitoring for production deployment:
1. Log monitoring with ELK stack or similar
2. Hardware health monitoring with Prometheus
3. Alert notifications for system failures
4. Performance metrics collection
5. Automated backup of configuration and logs
```

## Security Considerations

### Network Security

```bash
# Security best practices:
1. Use dedicated network segment for monitoring system
2. Configure firewall rules for required ports only
3. Enable WPA3 security for WiFi connections
4. Use VPN for remote access
5. Regular security updates for all components
```

### Physical Security

```bash
# Physical security measures:
1. Secure mounting for RTL-SDR and antennas
2. Tamper-evident enclosures for Pico W
3. Cable management and strain relief
4. Environmental protection (temperature, humidity)
5. Access control for system components
```

## Maintenance

### Regular Maintenance Tasks

```bash
# Weekly tasks:
1. Check system logs for errors
2. Verify hardware health status
3. Test system recovery mechanisms
4. Update system performance metrics
5. Backup configuration files

# Monthly tasks:
1. Update software dependencies
2. Run comprehensive system validation
3. Review and archive old log files
4. Test disaster recovery procedures
5. Update documentation as needed
```

### System Updates

```bash
# Update procedure:
1. Backup current configuration
2. Test updates in development environment
3. Schedule maintenance window
4. Apply updates with rollback plan
5. Verify system functionality
6. Update documentation
```

This comprehensive setup guide ensures reliable deployment and operation of the automotive security monitoring system with real hardware components.