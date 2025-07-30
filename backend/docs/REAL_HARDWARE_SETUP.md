# Real Hardware Setup Guide

This guide will help you test the Automotive Security System with your actual RTL-SDR V4 dongle and Raspberry Pi Pico 2 W with PN532 NFC chip.

## 🔧 Hardware Requirements

### RTL-SDR V4 Setup
- **Device**: RTL-SDR Blog V4 dongle
- **Driver**: Zadig WinUSB driver (Windows) or librtlsdr (Linux/Mac)
- **Antenna**: Telescopic antenna (included) or automotive-specific antenna
- **USB**: USB 3.0 port recommended for best performance

### Raspberry Pi Pico 2 W Setup
- **Device**: Raspberry Pi Pico 2 W with WiFi
- **NFC Module**: PN532 breakout board
- **Connection**: Breadboard with jumper wires
- **Power**: USB power or external 5V supply

### PN532 NFC Module Wiring
```
Pico 2 W    PN532 Module
--------    ------------
3V3         VCC
GND         GND
GPIO 4      SDA (I2C Data)
GPIO 5      SCL (I2C Clock)
```

## 🚀 Quick Start with Real Hardware

### Step 1: Verify RTL-SDR Connection
```bash
# Test RTL-SDR hardware detection
cd backend
uv run python -c "from hardware.rtl_sdr_interface import RTLSDRInterface; rtl = RTLSDRInterface(); print('Detection result:', rtl.detect_hardware())"
```

Expected output for working hardware:
```
RTL-SDR interface initialized with binary path: C:\...\backend\rtl_sdr_bin
Starting RTL-SDR hardware detection...
RTL-SDR detected: Realtek, RTL2838UHIDIR, SN: 00000001
Tuner: Rafael Micro R828D
Frequency range: 24.0 - 1766.0 MHz
Device supports automotive frequency bands
Detection result: True
```

### Step 2: Flash Pico 2 W Firmware
1. **Download MicroPython**: Get the latest Pico W firmware from [micropython.org](https://micropython.org/download/rp2-pico-w/)
2. **Flash Firmware**:
   - Hold BOOTSEL button while connecting USB
   - Copy `.uf2` file to RPI-RP2 drive
   - Device will reboot with MicroPython

3. **Deploy Code**: Use Thonny IDE (RECOMMENDED):

**STEP-BY-STEP DEPLOYMENT:**

1. **Install Thonny IDE**: Download from https://thonny.org/
2. **Connect Pico W**: 
   - Connect Pico W via USB to your computer
   - Open Thonny IDE
   - Go to Tools → Options → Interpreter
   - Select "MicroPython (Raspberry Pi Pico)"
   - Choose the correct COM port (e.g., COM3)
   - Click OK and wait for connection

3. **Configure Network Settings FIRST**:
   - Open `backend/pico/config.py` in any text editor
   - Update these lines:
     ```python
     WIFI_SSID = "YourActualWiFiName"     # Your WiFi network
     WIFI_PASSWORD = "YourActualPassword"  # Your WiFi password
     TCP_HOST = "192.168.1.XXX"           # Your computer's IP (from ipconfig)
     ```

4. **Upload Files in Order** (using Thonny):
   - **File 1**: Upload `config.py` first (small file, quick)
   - **File 2**: Upload `NFC_PN532.py` second (large file, be patient - may take 2-3 minutes)
   - **File 3**: Upload `main.py` last (medium file)

5. **Test the Connection**:
   - In Thonny's shell (bottom panel), type: `import main`
   - You should see WiFi connection messages
   - If successful, the Pico will connect to your computer automatically

**Alternative Methods** (if Thonny doesn't work):
```bash
# Command line deployment (may get stuck on large files)
cd backend
python deploy_pico.py COM3

# Using rshell (more reliable than our script)
pip install rshell
rshell -p COM3
> cp pico/config.py /pyboard/
> cp pico/NFC_PN532.py /pyboard/  # Be patient - large file
> cp pico/main.py /pyboard/
```

### Step 3: Configure Pico W Network
**IMPORTANT**: Before deploying, edit `backend/pico/config.py` with your network settings:
```python
# Network Configuration - UPDATE THESE
WIFI_SSID = "YourWiFiNetwork"        # Your WiFi network name
WIFI_PASSWORD = "YourWiFiPassword"   # Your WiFi password

# TCP Server Configuration - UPDATE THIS
TCP_HOST = "192.168.1.100"  # Your computer's IP address (find with ipconfig)
TCP_PORT = 8888

# Hardware Configuration
LED_PIN_RED = 15     # GPIO pin for red LED
LED_PIN_YELLOW = 14  # GPIO pin for yellow LED  
LED_PIN_GREEN = 13   # GPIO pin for green LED

# NFC Configuration
NFC_ENABLED = True   # Set to False if no NFC module
NFC_SDA_PIN = 4      # I2C SDA pin for PN532
NFC_SCL_PIN = 5      # I2C SCL pin for PN532
```

**Find Your Computer's IP Address**:
```bash
# Windows
ipconfig
# Look for "IPv4 Address" under your active network adapter

# Example output:
# IPv4 Address. . . . . . . . . . . : 192.168.1.100
```

### Step 4: Launch Real Hardware System
```bash
cd backend

# Launch with automatic hardware detection
uv run python real_hardware_launcher.py

# Or force demo mode for testing
uv run python real_hardware_launcher.py --force-mock

# Use specific frequency (315 MHz for North America)
uv run python real_hardware_launcher.py --frequency 315000000
```

### Step 5: Start Dashboard
In a separate terminal:
```bash
cd backend
uv run python cli_dashboard.py --source tcp --tcp-host localhost --tcp-port 8888
```

## 🔍 Testing Real Hardware

### RTL-SDR Testing
1. **Basic Hardware Test**:
```bash
# Test RTL-SDR directly
rtl_test -t

# Expected output:
# Found 1 device(s):
#   0:  Realtek, RTL2838UHIDIR, SN: 00000001
# Using device 0: Generic RTL2832U OEM
# Tuner: Rafael Micro R828D
```

2. **Frequency Scanning**:
```bash
# Scan automotive frequencies
rtl_power -f 315M:434M:1M -i 10 -g 25
```

3. **Manual Signal Capture**:
```bash
# Listen to 433.92 MHz (key fobs)
rtl_fm -f 433.92M -M fm -s 200k | aplay -r 22050 -f S16_LE
```

### Pico W + NFC Testing
1. **WiFi Connection**: Check Pico connects to your network
2. **TCP Connection**: Verify Pico connects to your computer
3. **NFC Detection**: Test with NFC cards/tags
4. **LED Alerts**: Verify LEDs respond to threat levels

### Integration Testing
1. **Key Fob Test**: Press car key fob near RTL-SDR antenna
2. **TPMS Test**: Use TPMS sensor or simulator
3. **NFC Test**: Bring NFC tag near PN532 module
4. **Multi-Modal Test**: Combine RF and NFC activity

## 📊 Expected Behavior

### Successful Startup Log
```
🚀 Starting Automotive Security Real Hardware System...
Step 1: Initializing hardware detection...
🔍 Detecting real hardware...
📊 Hardware Detection Results:
   System Status: ready
   RTL-SDR Status: configured
   RTL-SDR Device: Realtek, RTL2838UHIDIR, SN: 00000001
   Tuner Type: Rafael Micro R828D
   Frequency Range: 24.0 - 1766.0 MHz
   Pico W Status: 1 devices connected
🔧 System running with REAL HARDWARE
Step 2: Starting hardware monitoring...
Step 3: Starting RTL-SDR TCP server...
🎛️  RTL-SDR Configuration:
   Frequency: 433.920 MHz
   Sample Rate: 2.048 MS/s
   Gain: 25 dB
✅ RTL-TCP server started successfully
Step 4: Starting signal processing bridge...
✅ Signal processing bridge started
Step 5: Waiting for Pico W connections...
✅ 1 Pico W device(s) connected!
✅ Real hardware system startup complete!
```

### Dashboard with Real Signals
- **RF Events**: Real key fob presses, TPMS signals
- **Signal Analysis**: Actual RSSI, frequency, modulation data
- **NFC Correlation**: Real NFC tag detections
- **Multi-Modal Attacks**: Combined RF+NFC events

## 🛠️ Troubleshooting

### Unicode Encoding Issues (FIXED)
**Problem**: `UnicodeEncodeError: 'charmap' codec can't encode character`
**Solution**: This has been fixed by removing emoji characters from log messages. The system now uses plain text logging that works on all Windows systems.

### System Won't Exit (Ctrl+C)
**Problem**: System hangs when waiting for Pico W connections
**Solution**: 
- Wait for 30-second timeout to complete
- Use Ctrl+Break instead of Ctrl+C on Windows
- Close terminal window if completely stuck
- Ensure Pico W is properly configured and connecting

### RTL-SDR Issues
**Problem**: `No supported devices found`
**Solution**: 
- Check USB connection
- Install/update drivers with Zadig
- Try different USB port
- Verify device with `rtl_test`

**Problem**: `usb_claim_interface error`
**Solution**:
- Close other SDR software (SDR#, GQRX, etc.)
- Restart computer
- Check device permissions (Linux)

### Pico W Issues
**Problem**: Pico won't connect to WiFi
**Solution**:
- Check SSID/password in config.py
- Verify 2.4GHz network (Pico W doesn't support 5GHz)
- Check network security settings

**Problem**: TCP connection fails
**Solution**:
- Verify computer IP address
- Check firewall settings (allow port 8888)
- Ensure both devices on same network

### NFC Issues
**Problem**: PN532 not detected
**Solution**:
- Check I2C wiring (SDA/SCL pins)
- Verify 3.3V power connection
- Test with simple I2C scan

## 🎯 Performance Optimization

### RTL-SDR Settings
- **Sample Rate**: 2.048 MS/s for automotive (balance of coverage vs. processing)
- **Gain**: Auto or 25-35 dB (adjust based on environment)
- **Frequency**: 433.92 MHz (Europe) or 315 MHz (North America)

### System Resources
- **CPU**: Monitor usage, reduce sample rate if needed
- **Memory**: System uses ~100-200MB RAM
- **USB**: Use USB 3.0 for best performance

### Network Optimization
- **WiFi**: Use 2.4GHz for better range to Pico W
- **Bandwidth**: System uses minimal network traffic
- **Latency**: Keep Pico W close to router for best response

## 🔒 Security Considerations

### Network Security
- Use dedicated IoT network if available
- Change default passwords
- Monitor network traffic

### RF Safety
- Use appropriate antenna for frequency
- Follow local RF emission regulations
- Keep power levels reasonable

### Data Privacy
- All processing done locally
- No cloud data transmission
- Logs stored locally only

## 📈 Advanced Configuration

### Custom Frequencies
```python
# Edit real_hardware_launcher.py
AUTOMOTIVE_FREQUENCIES = {
    'key_fob_na': 315000000,      # North America
    'key_fob_eu': 433920000,      # Europe
    'tpms_na': 315000000,         # TPMS North America
    'tpms_eu': 433920000,         # TPMS Europe
    'ism_868': 868000000,         # ISM band
}
```

### Multiple RTL-SDR Devices
The system supports multiple RTL-SDR dongles for monitoring different frequencies simultaneously.

### Enhanced NFC Features
- Multiple PN532 modules
- Different NFC tag types
- Custom proximity thresholds

## 🎉 Success Indicators

You'll know the system is working when you see:
1. ✅ RTL-SDR detected and configured
2. ✅ Pico W connected with NFC active
3. ✅ Real RF signals in dashboard
4. ✅ NFC tags detected and correlated
5. ✅ LEDs responding to threat levels
6. ✅ Multi-modal attack detection working

## 📞 Support

If you encounter issues:
1. Check logs in `real_hardware_system.log`
2. Verify hardware connections
3. Test components individually
4. Use mock mode to isolate software issues

The system is designed to gracefully handle hardware failures and provide detailed diagnostics to help troubleshoot any issues.