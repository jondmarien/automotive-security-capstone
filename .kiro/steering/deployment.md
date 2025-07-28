# Deployment Guide & Production Considerations

## Deployment Architecture Overview

### System Deployment Models

#### 1. Development/Demo Deployment
- **Purpose**: Local development, testing, and demonstrations
- **Hardware**: Single development machine with RTL-SDR and Pico W
- **Network**: Local TCP connections (127.0.0.1)
- **Data**: Mock mode available for hardware-free demonstrations
- **Scalability**: Single user, limited concurrent operations

#### 2. Educational Lab Deployment
- **Purpose**: Classroom demonstrations and student experiments
- **Hardware**: Multiple RTL-SDR devices, shared Pico W units
- **Network**: Local network with multiple monitoring stations
- **Data**: Shared event logging and analysis
- **Scalability**: 10-20 concurrent users, centralized monitoring

#### 3. Research Deployment
- **Purpose**: Extended research projects and data collection
- **Hardware**: High-performance RTL-SDR devices, multiple Pico W units
- **Network**: Dedicated research network with external connectivity
- **Data**: Long-term data storage and analysis capabilities
- **Scalability**: Continuous operation, large-scale data processing

#### 4. Production-Ready Deployment (Future)
- **Purpose**: Commercial automotive security monitoring
- **Hardware**: Industrial-grade RF equipment, redundant systems
- **Network**: Secure enterprise network with monitoring and alerting
- **Data**: Enterprise database with backup and disaster recovery
- **Scalability**: High availability, load balancing, auto-scaling

## Hardware Deployment Configurations

### RTL-SDR Hardware Setup

#### Single RTL-SDR Configuration
```yaml
# config/single_rtl_sdr.yaml
rtl_sdr:
  device_index: 0
  frequency: 433920000      # 433.92 MHz (primary automotive frequency)
  sample_rate: 2048000      # 2.048 MS/s
  gain: "auto"              # Automatic gain control
  tcp_port: 1234           # Standard RTL-TCP port
  buffer_size: 262144      # 256KB buffer for smooth operation
```

#### Multi-RTL-SDR Configuration
```yaml
# config/multi_rtl_sdr.yaml
rtl_sdr_devices:
  - device_index: 0
    frequency: 315000000    # 315 MHz (North American key fobs, TPMS)
    sample_rate: 2048000
    tcp_port: 1234
    description: "315 MHz Monitor"
  
  - device_index: 1
    frequency: 433920000    # 433.92 MHz (European key fobs, TPMS)
    sample_rate: 2048000
    tcp_port: 1235
    description: "433 MHz Monitor"
  
  - device_index: 2
    frequency: 868000000    # 868 MHz (European ISM band)
    sample_rate: 2048000
    tcp_port: 1236
    description: "868 MHz Monitor"
```

#### Hardware Requirements by Deployment Type
```yaml
# Development Deployment
hardware_requirements:
  rtl_sdr:
    model: "RTL-SDR Blog V4"
    quantity: 1
    frequency_range: "500 kHz - 1.75 GHz"
    sample_rate: "up to 3.2 MS/s"
  
  pico_w:
    model: "Raspberry Pi Pico W"
    quantity: 1
    memory: "264KB SRAM"
    connectivity: "802.11n WiFi"
  
  development_machine:
    cpu: "Intel i5 or AMD Ryzen 5 (minimum)"
    ram: "8GB (minimum), 16GB (recommended)"
    storage: "10GB free space"
    usb: "USB 3.0 port for RTL-SDR"

# Educational Lab Deployment
lab_requirements:
  rtl_sdr:
    quantity: 5-10
    mounting: "USB hubs with individual power"
    antennas: "Telescopic antennas for each device"
  
  pico_w:
    quantity: 5-10
    mounting: "Breadboards or custom PCBs"
    indicators: "RGB LEDs for threat level indication"
  
  network:
    switch: "Gigabit Ethernet switch"
    wifi: "Dedicated WiFi network for Pico W devices"
    isolation: "Network isolation from main campus network"
```

### Raspberry Pi Pico W Deployment

#### Firmware Deployment Process
```bash
# 1. Prepare MicroPython Environment
# Download latest MicroPython firmware for Pico W
wget https://micropython.org/download/rp2-pico-w/rp2-pico-w-latest.uf2

# 2. Flash MicroPython Firmware
# Hold BOOTSEL button while connecting USB
# Copy firmware to RPI-RP2 drive
cp rp2-pico-w-latest.uf2 /media/RPI-RP2/

# 3. Deploy Application Code
# Use Thonny IDE or rshell for file transfer
rshell -p /dev/ttyACM0
> cp backend/pico/main.py /pyboard/
> cp backend/pico/NFC_PN532.py /pyboard/
> cp backend/pico/config.py /pyboard/
```

#### Pico W Configuration Management
```python
# backend/pico/config.py
"""Configuration management for Pico W deployment."""

# Network Configuration
WIFI_SSID = "automotive-security-lab"
WIFI_PASSWORD = "secure-password-here"

# TCP Server Configuration
TCP_HOST = "192.168.1.100"  # Main monitoring system IP
TCP_PORT = 8888             # Event server port
RECONNECT_INTERVAL = 5      # Seconds between connection attempts

# Hardware Configuration
LED_PIN_RED = 15           # GPIO pin for red LED (malicious threats)
LED_PIN_YELLOW = 14        # GPIO pin for yellow LED (suspicious activity)
LED_PIN_GREEN = 13         # GPIO pin for green LED (normal operation)
LED_BRIGHTNESS = 128       # PWM brightness (0-255)

# NFC Configuration
NFC_ENABLED = True
NFC_SDA_PIN = 4           # I2C SDA pin for NFC module
NFC_SCL_PIN = 5           # I2C SCL pin for NFC module

# Operational Parameters
HEARTBEAT_INTERVAL = 30    # Seconds between heartbeat messages
ALERT_TIMEOUT = 10         # Seconds to display alert before reset
DEBUG_MODE = False         # Enable debug output
```

## Network Architecture and Security

### Network Topology

#### Development Network (Local)
```
┌─────────────────┐    TCP:1234     ┌─────────────────┐
│   RTL-SDR V4    │◄──────────────►│  Development    │
│   (RF Capture)  │                │  Machine        │
└─────────────────┘                │  (Processing)   │
                                   └─────────────────┘
                                           │
                                           │ TCP:8888
                                           ▼
                                   ┌─────────────────┐
                                   │ Raspberry Pi    │
                                   │ Pico W          │
                                   │ (Alerts)        │
                                   └─────────────────┘
```

#### Lab Network (Multi-Station)
```
                    ┌─────────────────┐
                    │   Lab Router    │
                    │  192.168.1.1    │
                    └─────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │ Station 1   │ │ Station 2   │ │ Station N   │
    │192.168.1.10 │ │192.168.1.20 │ │192.168.1.N0 │
    └─────────────┘ └─────────────┘ └─────────────┘
            │               │               │
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │  Pico W 1   │ │  Pico W 2   │ │  Pico W N   │
    │192.168.1.11 │ │192.168.1.21 │ │192.168.1.N1 │
    └─────────────┘ └─────────────┘ └─────────────┘
```

### Network Security Configuration

#### Firewall Rules
```bash
# Linux iptables configuration for lab deployment
#!/bin/bash

# Allow RTL-TCP traffic (port 1234)
iptables -A INPUT -p tcp --dport 1234 -s 192.168.1.0/24 -j ACCEPT

# Allow event server traffic (port 8888)
iptables -A INPUT -p tcp --dport 8888 -s 192.168.1.0/24 -j ACCEPT

# Allow SSH for administration
iptables -A INPUT -p tcp --dport 22 -s 192.168.1.0/24 -j ACCEPT

# Block all other incoming traffic
iptables -A INPUT -j DROP

# Allow all outgoing traffic
iptables -A OUTPUT -j ACCEPT
```

#### Network Monitoring
```python
# backend/utils/network_monitor.py
"""Network monitoring and health checks for deployment."""

import asyncio
import socket
import logging
from typing import List, Dict, Any

class NetworkMonitor:
    """Monitor network connectivity and service health."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def check_rtl_tcp_connectivity(self) -> bool:
        """Check RTL-TCP server connectivity."""
        try:
            reader, writer = await asyncio.open_connection(
                self.config['rtl_tcp_host'],
                self.config['rtl_tcp_port']
            )
            writer.close()
            await writer.wait_closed()
            return True
        except Exception as e:
            self.logger.error(f"RTL-TCP connectivity check failed: {e}")
            return False
    
    async def check_pico_connectivity(self) -> List[str]:
        """Check Pico W device connectivity."""
        connected_devices = []
        
        for pico_config in self.config['pico_devices']:
            try:
                reader, writer = await asyncio.open_connection(
                    pico_config['ip'],
                    pico_config['port']
                )
                writer.close()
                await writer.wait_closed()
                connected_devices.append(pico_config['name'])
            except Exception as e:
                self.logger.warning(f"Pico W {pico_config['name']} not reachable: {e}")
        
        return connected_devices
```

## Service Management and Process Control

### Systemd Service Configuration (Linux)

#### RTL-SDR Service
```ini
# /etc/systemd/system/automotive-security-rtl.service
[Unit]
Description=Automotive Security RTL-SDR Server
After=network.target
Requires=network.target

[Service]
Type=simple
User=automotive-security
Group=automotive-security
WorkingDirectory=/opt/automotive-security/backend
Environment=PYTHONPATH=/opt/automotive-security/backend
ExecStart=/opt/automotive-security/.venv/bin/python rtl_sdr/startup_server.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# Resource limits
MemoryMax=1G
CPUQuota=50%

[Install]
WantedBy=multi-user.target
```

#### Detection Service
```ini
# /etc/systemd/system/automotive-security-detection.service
[Unit]
Description=Automotive Security Detection Engine
After=automotive-security-rtl.service
Requires=automotive-security-rtl.service

[Service]
Type=simple
User=automotive-security
Group=automotive-security
WorkingDirectory=/opt/automotive-security/backend
Environment=PYTHONPATH=/opt/automotive-security/backend
ExecStart=/opt/automotive-security/.venv/bin/python detection/security_analyzer.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# Resource limits
MemoryMax=2G
CPUQuota=75%

[Install]
WantedBy=multi-user.target
```

### Windows Service Configuration

#### NSSM (Non-Sucking Service Manager) Setup
```batch
REM Install NSSM service wrapper
nssm install "Automotive Security RTL" "C:\automotive-security\.venv\Scripts\python.exe"
nssm set "Automotive Security RTL" AppParameters "rtl_sdr\startup_server.py"
nssm set "Automotive Security RTL" AppDirectory "C:\automotive-security\backend"
nssm set "Automotive Security RTL" DisplayName "Automotive Security RTL-SDR Server"
nssm set "Automotive Security RTL" Description "RTL-SDR server for automotive security monitoring"
nssm set "Automotive Security RTL" Start SERVICE_AUTO_START

REM Start the service
nssm start "Automotive Security RTL"
```

### Docker Deployment (Advanced)

#### Dockerfile
```dockerfile
# Dockerfile for automotive security system
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    rtl-sdr \
    librtlsdr-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd -m -u 1000 automotive-security

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY config/ ./config/

# Set ownership
RUN chown -R automotive-security:automotive-security /app

# Switch to application user
USER automotive-security

# Expose ports
EXPOSE 1234 8888

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('localhost', 8888), timeout=5)"

# Start command
CMD ["python", "backend/rtl_sdr/startup_server.py"]
```

#### Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  automotive-security:
    build: .
    container_name: automotive-security
    restart: unless-stopped
    
    # Device access for RTL-SDR
    devices:
      - "/dev/bus/usb:/dev/bus/usb"
    
    # Privileged mode for USB access
    privileged: true
    
    # Port mapping
    ports:
      - "1234:1234"  # RTL-TCP
      - "8888:8888"  # Event server
    
    # Volume mounts
    volumes:
      - ./config:/app/config:ro
      - ./logs:/app/logs
      - ./data:/app/data
    
    # Environment variables
    environment:
      - LOG_LEVEL=INFO
      - CONFIG_FILE=/app/config/production.yaml
    
    # Resource limits
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
    
    # Health check
    healthcheck:
      test: ["CMD", "python", "-c", "import socket; socket.create_connection(('localhost', 8888), timeout=5)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Log aggregation (optional)
  fluentd:
    image: fluentd:v1.14
    container_name: automotive-security-logs
    volumes:
      - ./fluentd/conf:/fluentd/etc
      - ./logs:/var/log/automotive-security
    ports:
      - "24224:24224"
    depends_on:
      - automotive-security
```

## Monitoring and Alerting

### System Health Monitoring

#### Health Check Endpoints
```python
# backend/utils/health_check.py
"""System health monitoring and reporting."""

import asyncio
import psutil
import time
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class SystemHealth:
    """System health status information."""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_connectivity: bool
    rtl_sdr_status: bool
    pico_connectivity: int
    uptime: float
    last_event_time: float

class HealthMonitor:
    """Monitor system health and generate status reports."""
    
    def __init__(self):
        self.start_time = time.time()
        self.last_event_time = time.time()
    
    async def get_system_health(self) -> SystemHealth:
        """Get comprehensive system health status."""
        # CPU and memory usage
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network connectivity
        network_ok = await self._check_network_connectivity()
        
        # RTL-SDR status
        rtl_sdr_ok = await self._check_rtl_sdr_status()
        
        # Pico W connectivity
        pico_count = await self._count_connected_picos()
        
        # System uptime
        uptime = time.time() - self.start_time
        
        return SystemHealth(
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            network_connectivity=network_ok,
            rtl_sdr_status=rtl_sdr_ok,
            pico_connectivity=pico_count,
            uptime=uptime,
            last_event_time=self.last_event_time
        )
```

#### Alerting Configuration
```yaml
# config/alerting.yaml
alerting:
  enabled: true
  
  # Alert thresholds
  thresholds:
    cpu_usage: 80.0          # Percent
    memory_usage: 85.0       # Percent
    disk_usage: 90.0         # Percent
    event_timeout: 300       # Seconds without events
  
  # Alert channels
  channels:
    email:
      enabled: true
      smtp_server: "smtp.university.edu"
      smtp_port: 587
      username: "automotive-security@university.edu"
      recipients:
        - "admin@university.edu"
        - "professor@university.edu"
    
    slack:
      enabled: false
      webhook_url: "https://hooks.slack.com/services/..."
      channel: "#automotive-security"
    
    syslog:
      enabled: true
      facility: "local0"
      severity: "warning"
```

### Log Management

#### Centralized Logging Configuration
```python
# backend/utils/logging_config.py
"""Centralized logging configuration for deployment."""

import logging
import logging.handlers
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add custom fields
        if hasattr(record, 'threat_level'):
            log_entry['threat_level'] = record.threat_level
        if hasattr(record, 'frequency'):
            log_entry['frequency'] = record.frequency
        
        return json.dumps(log_entry)

def setup_logging(config: Dict[str, Any]):
    """Setup logging configuration for deployment."""
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config['log_level']))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        config['log_file'],
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)
    
    # Syslog handler (for production)
    if config.get('syslog_enabled', False):
        syslog_handler = logging.handlers.SysLogHandler(
            address=config['syslog_address']
        )
        syslog_handler.setFormatter(logging.Formatter(
            'automotive-security: %(name)s - %(levelname)s - %(message)s'
        ))
        root_logger.addHandler(syslog_handler)
```

## Backup and Disaster Recovery

### Data Backup Strategy
```bash
#!/bin/bash
# backup_system.sh - Automated backup script

BACKUP_DIR="/backup/automotive-security"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/backup_$DATE"

# Create backup directory
mkdir -p "$BACKUP_PATH"

# Backup configuration files
cp -r /opt/automotive-security/config "$BACKUP_PATH/"

# Backup logs (last 30 days)
find /opt/automotive-security/logs -name "*.log" -mtime -30 -exec cp {} "$BACKUP_PATH/logs/" \;

# Backup recorded signals
cp -r /opt/automotive-security/backend/rtl_sdr/recordings "$BACKUP_PATH/"

# Create archive
tar -czf "$BACKUP_PATH.tar.gz" -C "$BACKUP_DIR" "backup_$DATE"

# Remove uncompressed backup
rm -rf "$BACKUP_PATH"

# Keep only last 7 backups
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_PATH.tar.gz"
```

### Disaster Recovery Procedures
```markdown
# Disaster Recovery Procedures

## System Failure Recovery

### 1. Hardware Failure
- **RTL-SDR Failure**: Replace device, verify with `rtl_test`
- **Pico W Failure**: Reflash firmware, reconfigure network
- **Server Failure**: Restore from backup, verify configuration

### 2. Software Failure
- **Service Crash**: Restart services with systemctl
- **Configuration Corruption**: Restore from backup
- **Database Issues**: Rebuild from logs if needed

### 3. Network Failure
- **Connectivity Loss**: Check network configuration
- **Port Conflicts**: Verify port availability
- **Firewall Issues**: Review firewall rules

## Recovery Steps

1. **Assess Damage**: Determine scope of failure
2. **Restore Backup**: Deploy latest known-good configuration
3. **Verify Hardware**: Test all hardware components
4. **Restart Services**: Bring system back online
5. **Validate Operation**: Confirm normal operation
6. **Document Incident**: Record lessons learned
```

This comprehensive deployment guide ensures reliable, scalable deployment of the automotive security monitoring system across various environments, from development to production-ready installations.