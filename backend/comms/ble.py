"""
BLE server implementation for automotive security dongle using bless.
Exposes a characteristic for sending security alerts to a mobile app client.
"""

import sys
import logging
import asyncio
import threading
from typing import Any, Union
from bless import (
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions,
)

# Configure logging for BLE server events and debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use appropriate synchronization primitive for cross-platform compatibility
# - threading.Event on macOS/Windows (required by some BLE stacks)
# - asyncio.Event on Linux
trigger: Union[asyncio.Event, threading.Event]
if sys.platform in ["darwin", "win32"]:
    trigger = threading.Event()
else:
    trigger = asyncio.Event()

# UUIDs for the BLE service and characteristic
# These should be replaced with project-specific UUIDs for production
ALERT_SERVICE_UUID = "A07498CA-AD5B-474E-940D-16F1FBE7E8CD"
ALERT_CHAR_UUID = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"

# This variable holds the latest alert value (as bytes) for the characteristic
alert_value = b"No alert"

def read_alert(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
    """
    Handle read requests from the client (mobile app).
    Returns the current value of the alert characteristic.
    """
    logger.info(f"Reading alert: {characteristic.value}")
    return characteristic.value

def write_alert(characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
    """
    Handle write requests from the client (mobile app).
    Updates the alert characteristic value and triggers event if acknowledged.
    """
    characteristic.value = value
    logger.info(f"Alert characteristic updated: {characteristic.value}")
    # If the client writes 'ack', treat it as an acknowledgment of alert receipt
    if characteristic.value == b"ack":
        logger.info("Alert acknowledged by client.")
        trigger.set()

async def start_ble_server(loop, initial_alert=b"No alert"):
    """
    Start the BLE server, advertise the alert service and characteristic.
    Waits for the client to connect and interact with the characteristic.
    Args:
        loop: The asyncio event loop
        initial_alert (bytes): Initial value for the alert characteristic
    """
    global alert_value
    alert_value = initial_alert
    trigger.clear()
    # Instantiate the BLE server with a device name
    server = BlessServer(name="AutoSecDongle", loop=loop)
    # Register read/write callbacks
    server.read_request_func = read_alert
    server.write_request_func = write_alert
    # Add a custom service for alerts
    await server.add_new_service(ALERT_SERVICE_UUID)
    # Add a characteristic with read, write, and indicate properties
    char_flags = (
        GATTCharacteristicProperties.read
        | GATTCharacteristicProperties.write
        | GATTCharacteristicProperties.indicate
    )
    permissions = GATTAttributePermissions.readable | GATTAttributePermissions.writeable
    await server.add_new_characteristic(
        ALERT_SERVICE_UUID, ALERT_CHAR_UUID, char_flags, alert_value, permissions
    )
    logger.info("BLE server starting, advertising security alert characteristic...")
    await server.start()
    # Wait for the client to acknowledge (or for the event to be set)
    if trigger.__module__ == "threading":
        trigger.wait()
    else:
        await trigger.wait()
    await asyncio.sleep(1)
    await server.stop()

async def update_alert(new_alert: bytes, loop=None):
    """
    Update the alert characteristic value (to be called when a new alert is available).
    Args:
        new_alert (bytes): The new alert value to send to the client
        loop: The asyncio event loop (optional)
    Note: In a full implementation, this would notify the client using BLE indications.
    """
    global alert_value
    alert_value = new_alert
    # In a production implementation, notify the client here
    logger.info(f"Alert updated: {new_alert}")
    # This is a placeholder; integrate with BlessServer instance as needed

# If run as a script, start the BLE server for testing
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_ble_server(loop, b"Test alert"))


def send_ble_alert(*args, **kwargs):
    """
    Stub for sending a BLE alert. Replace with real implementation.
    """
    logger.info("send_ble_alert called (stub)")
    pass