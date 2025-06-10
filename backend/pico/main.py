import network
import socket
import json
import time
import NFC_PN532 as nfc  # type: ignore

# ==== CONFIGURATION ====
SSID = "Jon's Pixel 8 Pro"
PASSWORD = "password"
SERVER_IP = "10.237.74.73"  # <-- your computer's IP
SERVER_PORT = 8888

# ==== WIFI CONNECTION ====
def connect_wifi():
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
                        # Here you can add logic to handle detection events, trigger LEDs, etc.
                    except Exception as e:
                        print("Invalid JSON:", e)
    except Exception as e:
        print("Error in main loop:", e)
    finally:
        sock.close()
        print("Disconnected from server.")

if __name__ == "__main__":
    main()