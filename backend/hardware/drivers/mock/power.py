"""Mock implementation of the power management interface."""
import asyncio
import logging
from typing import Optional

from hardware.interfaces.power import PowerInterface
from hardware.models.models import PowerState

logger = logging.getLogger(__name__)


class MockPowerInterface(PowerInterface):
    """Mock implementation of the power management interface.
    
    This implementation simulates a power management interface for testing purposes.
    It maintains an internal state for power status and battery level.
    """
    
    def __init__(self):
        """Initialize the mock power interface."""
        self._power_state = PowerState.ACTIVE
        self._battery_level = 0.8  # 80% by default
        self._charging = False
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the power interface."""
        self._initialized = True
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        self._initialized = False
    
    def set_power_state(self, state: PowerState) -> None:
        """Set the power state of the device."""
        if not self._initialized:
            raise RuntimeError("Power interface not initialized")
        self._power_state = state
    
    def get_power_state(self) -> PowerState:
        """Get the current power state."""
        if not self._initialized:
            raise RuntimeError("Power interface not initialized")
        return self._power_state
    
    def get_battery_level(self) -> float:
        """Get the current battery level (0.0 to 1.0)."""
        if not self._initialized:
            raise RuntimeError("Power interface not initialized")
        return self._battery_level
    
    def is_charging(self) -> bool:
        """Check if the device is currently charging."""
        if not self._initialized:
            raise RuntimeError("Power interface not initialized")
        return self._charging
    
    def get_power_source(self) -> str:
        """Get the current power source."""
        if not self._initialized:
            raise RuntimeError("Power interface not initialized")
        return "battery" if not self._charging else "usb"
    
    def get_voltage(self) -> float:
        """Get the current voltage in volts."""
        if not self._initialized:
            raise RuntimeError("Power interface not initialized")
        return 3.7  # Typical LiPo voltage
    
    def get_current(self) -> float:
        """Get the current current in amps."""
        if not self._initialized:
            raise RuntimeError("Power interface not initialized")
        return 0.1  # 100mA
    
    def get_temperature(self) -> float:
        """Get the current temperature in degrees Celsius."""
        if not self._initialized:
            raise RuntimeError("Power interface not initialized")
        return 25.0  # Room temperature
        
    async def reboot(self) -> None:
        """Reboot the device.
        
        Raises:
            RuntimeError: If the power interface is not initialized
        """
        if not self._initialized:
            raise RuntimeError("Power interface not initialized")
        logger.info("Mock device rebooting...")
        # In a real implementation, this would trigger a system reboot
        
    async def shutdown(self) -> None:
        """Shut down the device.
        
        Raises:
            RuntimeError: If the power interface is not initialized
        """
        if not self._initialized:
            raise RuntimeError("Power interface not initialized")
        logger.info("Mock device shutting down...")
        # In a real implementation, this would power off the system
