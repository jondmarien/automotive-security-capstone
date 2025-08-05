"""
Configuration for Raspberry Pi Pico W
Update these settings for your network and system.
"""

# WiFi Configuration - UPDATE THESE FOR YOUR NETWORK
WIFI_SSID = "Office 2"  # Replace with your WiFi network name
WIFI_PASSWORD = "CJutHW3vt@"  # Replace with your WiFi password

# Server Configuration - UPDATE THIS FOR YOUR COMPUTER'S IP
TCP_HOST = "192.168.2.250"  # Replace with your computer's IP address
TCP_PORT = 8888  # Event server port (should match real_hardware_launcher.py)
RECONNECT_INTERVAL = 5  # Seconds between connection attempts

# Hardware Configuration
LED_PIN_RED = 15  # GPIO pin for red LED (malicious threats)
LED_PIN_YELLOW = 14  # GPIO pin for yellow LED (suspicious activity)
LED_PIN_GREEN = 13  # GPIO pin for green LED (normal operation)
LED_BRIGHTNESS = 128  # PWM brightness (0-255)

# NFC Configuration (if NFC module is connected)
NFC_ENABLED = True  # Set to True if you have NFC module connected
NFC_SDA_PIN = 4  # I2C SDA pin for NFC module
NFC_SCL_PIN = 5  # I2C SCL pin for NFC module

# Operational Parameters
HEARTBEAT_INTERVAL = 30  # Seconds between heartbeat messages
ALERT_TIMEOUT = 10  # Seconds to display alert before reset
DEBUG_MODE = True  # Enable debug output

# Network timeout settings
WIFI_TIMEOUT = 30  # Seconds to wait for WiFi connection
TCP_TIMEOUT = 10  # Seconds to wait for TCP connection
