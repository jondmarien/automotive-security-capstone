#!/usr/bin/env python3
"""
Pico W Deployment Script
Deploys MicroPython code to Raspberry Pi Pico W via serial connection.
"""

import os
import sys
import time
import serial
import serial.tools.list_ports
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PicoDeployer:
    """Deploy code to Raspberry Pi Pico W."""
    
    def __init__(self, port=None, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.connection = None
        
    def find_pico_port(self):
        """Find Pico W serial port automatically."""
        logger.info("Scanning for Pico W devices...")
        
        ports = serial.tools.list_ports.comports()
        pico_ports = []
        
        for port in ports:
            # Look for Pico W identifiers
            if any(identifier in str(port).lower() for identifier in ['pico', 'rp2040', 'micropython']):
                pico_ports.append(port.device)
                logger.info(f"Found potential Pico W on {port.device}: {port.description}")
        
        # Also check common Windows COM ports
        for i in range(1, 20):
            port_name = f"COM{i}"
            try:
                with serial.Serial(port_name, self.baudrate, timeout=1) as test_conn:
                    test_conn.write(b'\r\n')
                    time.sleep(0.1)
                    response = test_conn.read_all()
                    if b'>>>' in response or b'MicroPython' in response:
                        pico_ports.append(port_name)
                        logger.info(f"Found MicroPython on {port_name}")
            except (serial.SerialException, OSError):
                continue
        
        return pico_ports
    
    def connect(self):
        """Connect to Pico W."""
        if not self.port:
            ports = self.find_pico_port()
            if not ports:
                logger.error("No Pico W devices found!")
                return False
            self.port = ports[0]
            logger.info(f"Using port: {self.port}")
        
        try:
            self.connection = serial.Serial(self.port, self.baudrate, timeout=2)
            time.sleep(2)  # Wait for connection to stabilize
            
            # Test connection
            self.connection.write(b'\r\n')
            time.sleep(0.5)
            response = self.connection.read_all().decode('utf-8', errors='ignore')
            
            if '>>>' in response or 'MicroPython' in response:
                logger.info("Successfully connected to Pico W")
                return True
            else:
                logger.warning(f"Connected but no MicroPython prompt found. Response: {response}")
                return True  # Continue anyway
                
        except Exception as e:
            logger.error(f"Failed to connect to {self.port}: {e}")
            return False
    
    def send_command(self, command, wait_for_response=True):
        """Send command to Pico W and get response."""
        if not self.connection:
            logger.error("Not connected to Pico W")
            return None
        
        try:
            # Clear any existing data
            self.connection.read_all()
            
            # Send command
            self.connection.write(command.encode() + b'\r\n')
            
            if wait_for_response:
                time.sleep(0.5)
                response = self.connection.read_all().decode('utf-8', errors='ignore')
                return response
            
        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            return None
    
    def upload_file(self, local_path, remote_path):
        """Upload a file to Pico W."""
        logger.info(f"Uploading {local_path} -> {remote_path}")
        
        if not os.path.exists(local_path):
            logger.error(f"Local file not found: {local_path}")
            return False
        
        try:
            with open(local_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prepare the file upload command
            upload_cmd = f"""
with open('{remote_path}', 'w') as f:
    f.write('''{content}''')
"""
            
            # Send the upload command
            response = self.send_command(upload_cmd)
            
            if response and 'Traceback' not in response:
                logger.info(f"Successfully uploaded {remote_path}")
                return True
            else:
                logger.error(f"Upload failed: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to upload {local_path}: {e}")
            return False
    
    def list_files(self):
        """List files on Pico W."""
        response = self.send_command("import os; print(os.listdir('/'))")
        if response:
            logger.info(f"Files on Pico W: {response}")
        return response
    
    def reboot(self):
        """Reboot Pico W."""
        logger.info("Rebooting Pico W...")
        self.send_command("import machine; machine.reset()", wait_for_response=False)
        time.sleep(3)
    
    def disconnect(self):
        """Disconnect from Pico W."""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from Pico W")

def main():
    """Main deployment function."""
    logger.info("Pico W Deployment Tool")
    logger.info("=" * 50)
    
    # Check if port specified as argument
    port = None
    if len(sys.argv) > 1:
        port = sys.argv[1]
        logger.info(f"Using specified port: {port}")
    
    # Initialize deployer
    deployer = PicoDeployer(port=port)
    
    # Connect to Pico W
    if not deployer.connect():
        logger.error("Failed to connect to Pico W")
        return False
    
    try:
        # List current files
        deployer.list_files()
        
        # Files to deploy
        pico_dir = Path(__file__).parent / "pico"
        files_to_deploy = [
            ("config.py", "config.py"),      # Deploy config first
            ("NFC_PN532.py", "NFC_PN532.py"), # Then NFC library
            ("main.py", "main.py"),          # Finally main application
        ]
        
        # Check if config file has been customized
        config_path = pico_dir / "config.py"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config_content = f.read()
                if "YOUR_WIFI_NETWORK_NAME" in config_content:
                    logger.warning("WARNING: config.py still contains default values!")
                    logger.warning("Please update WIFI_SSID, WIFI_PASSWORD, and TCP_HOST in config.py")
                    logger.warning("Deployment will continue, but Pico W won't connect without proper config.")
        
        # Deploy each file
        success_count = 0
        for local_file, remote_file in files_to_deploy:
            local_path = pico_dir / local_file
            if deployer.upload_file(str(local_path), remote_file):
                success_count += 1
        
        logger.info(f"Deployment complete: {success_count}/{len(files_to_deploy)} files uploaded")
        
        # List files after deployment
        logger.info("Files after deployment:")
        deployer.list_files()
        
        # Reboot to start the new code
        deployer.reboot()
        
        logger.info("Pico W deployment completed successfully!")
        logger.info("The Pico W should now attempt to connect to WiFi and the main system.")
        
        return True
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        return False
        
    finally:
        deployer.disconnect()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)