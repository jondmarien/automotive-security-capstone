"""Power management interface definitions."""
from abc import ABC, abstractmethod

from ..models.models import PowerState


class PowerInterface(ABC):
    """Abstract base class for power management."""

    @abstractmethod
    def set_power_state(self, state: PowerState) -> None:
        """Set the power state of the device.
        
        Args:
            state: Desired power state
            
        Raises:
            HardwareError: If the power state cannot be set
        """
        pass

    @abstractmethod
    def get_power_state(self) -> PowerState:
        """Get the current power state.
        
        Returns:
            PowerState: Current power state
            
        Raises:
            HardwareError: If the power state cannot be determined
        """
        pass

    @abstractmethod
    def get_battery_level(self) -> float:
        """Get the current battery level.
        
        Returns:
            float: Battery level as a value between 0.0 (empty) and 1.0 (full)
            
        Raises:
            HardwareError: If the battery level cannot be read
        """
        pass

    @abstractmethod
    def is_charging(self) -> bool:
        """Check if the device is currently charging.
        
        Returns:
            bool: True if charging, False otherwise
            
        Raises:
            HardwareError: If the charging status cannot be determined
        """
        pass

    @abstractmethod
    def get_power_source(self) -> str:
        """Get the current power source.
        
        Returns:
            str: Power source (e.g., 'battery', 'usb', 'external')
            
        Raises:
            HardwareError: If the power source cannot be determined
        """
        pass

    @abstractmethod
    async def shutdown(self, force: bool = False) -> None:
        """Shut down the device.
        
        Args:
            force: If True, force immediate shutdown without cleanup
            
        Raises:
            HardwareError: If the device cannot be shut down
        """
        pass

    @abstractmethod
    async def reboot(self) -> None:
        """Reboot the device.
        
        Raises:
            HardwareError: If the device cannot be rebooted
        """
        pass
