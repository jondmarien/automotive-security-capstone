# Deployment Guide for Final Report

This section covers the deployment of the automotive security monitoring system for production and demonstration environments.

## Deployment Overview

The automotive security monitoring system supports multiple deployment configurations:

1. **Demo Mode** - Hardware-free demonstration for presentations
2. **Development Mode** - Local development with real or mock hardware
3. **Production Mode** - Full system deployment with hardware management
4. **Educational Lab** - Multi-station classroom deployment

## Hardware Requirements

### Core Components

| Component | Specification | Purpose | Cost |
|-----------|---------------|---------|------|
| RTL-SDR V4 | R828D tuner + RTL2832U, USB 3.0 | RF signal capture (500 kHz - 1.75 GHz) | ~$30 |
| Raspberry Pi Pico W | RP2040 MCU, 802.11n WiFi | Alert controller and NFC interface | ~$6 |
| PN532 NFC Module | 13.56 MHz NFC/RFID, SPI interface | Proximity detection (optional) | ~$8 |

### System Architecture

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

### Prerequisites

**Windows:**
- Python 3.11+
- RTL-SDR drivers (Zadig for USB driver management)
- RTL-SDR tools (included in `backend/rtl_sdr_bin/`)

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install rtl-sdr librtlsdr-dev python3.11 python3.11-venv
```

### Environment Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (UV recommended)
uv venv
uv pip install -r requirements.txt

# Alternative with pip
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux
pip install -r requirements.txt
```

### Hardware Verification

```bash
# Test RTL-SDR detection
rtl_test

# Test Python hardware interface
uv run python -c "from hardware.rtl_sdr_interface import RTLSDRInterface; rtl = RTLSDRInterface(); print('Detected:', rtl.detect_hardware())"
```

## Pico W Deployment

### Firmware Installation

1. **Download MicroPython firmware** for Pico W from micropython.org
2. **Flash firmware**: Hold BOOTSEL button while connecting USB, copy firmware to RPI-RP2 drive
3. **Deploy application code** using automated script:

```bash
# Automatic deployment with port detection
uv run python deploy_pico.py

# Manual port specification
uv run python deploy_pico.py COM3      # Windows
uv run python deploy_pico.py /dev/ttyACM0  # Linux
```

### Network Configuration

Edit `backend/pico/config.py`:

```python
# Network Configuration
WIFI_SSID = "your_network_name"
WIFI_PASSWORD = "your_wifi_password"

# TCP Server Configuration
TCP_HOST = "192.168.1.100"  # Your computer's IP address
TCP_PORT = 8888             # Event server port
```

## Deployment Modes

### 1. Demo Mode (Recommended for Presentations)

**Purpose**: Hardware-free demonstration with realistic automotive security events

```bash
# Basic demo with realistic events
uv run python cli_dashboard.py --mock

# Advanced demo with synthetic signal generation
uv run python cli_dashboard.py --mock --synthetic

# View specific event for detailed analysis
uv run python cli_dashboard.py --mock --event 3
```

**Features**:
- No hardware required
- Realistic automotive security events
- Professional CLI dashboard
- Event navigation and technical evidence display
- Perfect for capstone presentations

### 2. Complete System Deployment

**Purpose**: Full system with automatic hardware detection and recovery

```bash
# Launch with automatic hardware detection
uv run python real_hardware_launcher.py

# Force demo mode for presentations (system-wide)
uv run python real_hardware_launcher.py --force-mock

# Custom frequency configuration (315MHz for North America)
uv run python real_hardware_launcher.py --frequency 315000000
```

**Features**:
- Automatic RTL-SDR detection and configuration
- Pico W connection management with auto-reconnection
- Hardware failure recovery with exponential backoff
- Graceful fallback to mock mode if hardware unavailable
- Comprehensive logging and health monitoring

### 3. Manual Component Launch (Legacy)

**Purpose**: Individual component control for development and debugging

```bash
# Terminal 1: Start RTL-SDR server
uv run python rtl_sdr/rtl_tcp_server.py

# Terminal 2: Start signal processing
uv run python rtl_sdr/signal_bridge.py --enhanced

# Terminal 3: Start CLI dashboard
uv run python cli_dashboard.py --source tcp --tcp-host localhost --tcp-port 8888
```

## Hardware Management Features

### Automatic Detection and Configuration

The system includes comprehensive hardware management:

1. **RTL-SDR Detection**: Uses `rtl_test` to detect connected devices
2. **Capability Assessment**: Determines frequency range and supported features
3. **Automotive Configuration**: Optimizes settings for key fob monitoring (433.92 MHz EU / 315 MHz US)
4. **Health Monitoring**: Continuous hardware health checks every 15 seconds
5. **Failure Recovery**: Automatic recovery with exponential backoff (max 5 attempts)
6. **Mock Fallback**: Graceful fallback to demonstration mode if hardware fails

### Performance Targets

| Metric | Target | Purpose |
|--------|--------|---------|
| Hardware Detection | <5 seconds | Fast system startup |
| Signal Processing | <100ms latency | Real-time threat detection |
| Event Generation | <50ms | Immediate alert response |
| Recovery Time | <30 seconds | Minimal downtime |
| Memory Usage | <100MB | Efficient resource usage |
| CPU Usage | <25% | System responsiveness |

## Network Configuration

### Port Configuration

| Port | Service | Purpose |
|------|---------|---------|
| 1234 | RTL-TCP Server | IQ data streaming (internal) |
| 8888 | Event Server | TCP event distribution |

### Firewall Configuration

```bash
# Allow event server traffic (port 8888)
# Windows Firewall
netsh advfirewall firewall add rule name="Automotive Security" dir=in action=allow protocol=TCP localport=8888

# Linux iptables
sudo iptables -A INPUT -p tcp --dport 8888 -s 192.168.1.0/24 -j ACCEPT
```

## Deployment Verification

### System Health Check

```bash
# Comprehensive system diagnostics
uv run python -c "
from hardware import HardwareManager
import asyncio
import json

async def test():
    manager = HardwareManager()
    success = await manager.initialize()
    health = manager.get_health_status()
    print(f'System Status: {health.system_status.value}')
    print(f'RTL-SDR: {health.rtl_sdr_status.value}')
    print(f'Pico W: {health.pico_connections}/{health.total_pico_devices}')
    print(f'Uptime: {health.uptime:.1f}s')

asyncio.run(test())
"
```

### End-to-End Testing

```bash
# 1. Quick Demo Test (RECOMMENDED for initial verification)
uv run python cli_dashboard.py --mock

# 2. Advanced Demo Test with synthetic signals
uv run python cli_dashboard.py --mock --synthetic

# 3. Full System Test with Real Hardware
uv run python real_hardware_launcher.py

# 4. Verify dashboard connection (separate terminal)
uv run python cli_dashboard.py --source tcp
```

## Production Deployment

### Linux Service Configuration

```bash
# Create systemd service file
sudo nano /etc/systemd/system/automotive-security.service
```

```ini
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
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable automotive-security
sudo systemctl start automotive-security
sudo systemctl status automotive-security
```

### Windows Service Configuration

Using NSSM (Non-Sucking Service Manager):

```batch
# Install NSSM service wrapper
nssm install "Automotive Security" "C:\automotive-security\.venv\Scripts\python.exe"
nssm set "Automotive Security" AppParameters "real_hardware_launcher.py"
nssm set "Automotive Security" AppDirectory "C:\automotive-security\backend"
nssm set "Automotive Security" DisplayName "Automotive Security Monitor"
nssm set "Automotive Security" Start SERVICE_AUTO_START

# Start the service
nssm start "Automotive Security"
```

## Troubleshooting

### Common Issues and Solutions

**RTL-SDR Not Detected:**
1. Check USB connection (use USB 3.0 port if available)
2. Verify driver installation: `rtl_test`
3. Check device permissions (Linux): `sudo usermod -a -G plugdev $USER`
4. Use `--force-mock` for demo mode

**Pico W Connection Issues:**
1. Verify WiFi credentials in `config.py`
2. Check WiFi network (2.4GHz required)
3. Ensure computer and Pico on same network
4. Check firewall settings (allow port 8888)

**Performance Issues:**
1. Close unnecessary applications
2. Check system resources (CPU, memory)
3. Use SSD for better I/O performance
4. Optimize buffer sizes if needed

### Diagnostic Commands

```bash
# Real-time system health monitoring
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

## Security Considerations

### Network Security
- Use dedicated network segment for monitoring system
- Configure firewall rules for required ports only (8888)
- Enable WPA3 security for WiFi connections
- Regular security updates for all components

### Physical Security
- Secure mounting for RTL-SDR and antennas
- Tamper-evident enclosures for Pico W
- Cable management and strain relief
- Environmental protection (temperature, humidity)

## Maintenance

### Regular Tasks

**Weekly:**
- Check system logs for errors
- Verify hardware health status
- Test system recovery mechanisms
- Backup configuration files

**Monthly:**
- Update software dependencies
- Run comprehensive system validation
- Review and archive old log files
- Test disaster recovery procedures

### Log Management

System logs are organized by date in the `logs/` directory:

```
logs/
├── dashboard-2025-07-31/
│   ├── dashboard-09-30-15.log
│   └── dashboard-10-45-22.log
├── real_hardware_system.log
└── validation_20250731_123456/
    ├── accuracy_results.md
    └── confusion_matrix.png
```

This deployment guide ensures reliable operation of the automotive security monitoring system across various environments, from development to production deployments.