"""
main.py (Pico Client)

MicroPython code for Raspberry Pi Pico W.
Connects to WiFi and a backend TCP event server to receive automotive security detection events.
Handles event parsing and can trigger hardware actions (LED, buzzer, NFC, etc.).

Designed for use in the Automotive Security Capstone POC project.

Example usage:
    Copy this file to your Pico, set SSID/PASSWORD/SERVER_IP, and run main().
"""
import network
import socket
import json
import time
import NFC_PN532 as nfc  # type: ignore

# ==== CONFIGURATION ====
SSID = "Jon's Pixel 8 Pro"  # WiFi SSID
PASSWORD = "password"       # WiFi password
SERVER_IP = "10.237.74.73"  # <-- your computer's IP
SERVER_PORT = 8888           # TCP port for event server

# ==== WIFI CONNECTION ====
def connect_wifi():
    """
    Connect to WiFi using the configured SSID and PASSWORD.

    Returns:
        bool: True if connected, False otherwise.

    Example:
        if not connect_wifi():
            print("WiFi failed!")
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Connecting to WiFi...", end="")
    for _ in range(20):
        if wlan.isconnected():
            break
        print(".", end="")
        time.sleep(1)
    if wlan.isconnected():
        print("\nConnected! IP:", wlan.ifconfig()[0])
        return True
    else:
        print("\nFailed to connect.")
        return False

# ==== TCP CLIENT ====
def connect_to_server():
    """
    Connect to the backend TCP event server.

    Returns:
        socket.socket or None: Connected socket if successful, else None.

    Example:
        sock = connect_to_server()
        if not sock:
            print("Failed to connect!")
    """
    try:
        sock = socket.socket()
        sock.connect((SERVER_IP, SERVER_PORT))
        print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")
        return sock
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        return None

# ==== MAIN LOOP ====
def main():
    """
    Main Pico client loop. Connects to WiFi and event server, receives and parses detection events.
    Extend this function to trigger LEDs, buzzers, NFC, etc. on event.

    Example:
        main()
    """
    if not connect_wifi():
        return

    sock = connect_to_server()
    if not sock:
        return

    buffer = ""
    try:
        while True:
            data = sock.recv(1024)
            if not data:
                print("Server closed connection.")
                break
            buffer += data.decode()
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                if line.strip():
                    try:
                        event = json.loads(line)
                        print("Received event:", event)
                        # TODO: add logic to handle detection events
                    except Exception as e:
                        print("Invalid JSON:", e)
    except Exception as e:
        print("Error in main loop:", e)
    finally:
        sock.close()
        print("Disconnected from server.")

if __name__ == "__main__":
    main()