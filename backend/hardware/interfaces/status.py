"""Hardware status interface definitions."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict

from ..exceptions.exceptions import HardwareError
from ..models.models import MemoryUsage


class StatusInterface(ABC):
    """Abstract base class for hardware status monitoring."""

    @abstractmethod
    def get_temperature(self) -> float:
        """Get the current device temperature.
        
        Returns:
            float: Temperature in degrees Celsius
            
        Raises:
            HardwareError: If the temperature cannot be read
        """
        pass

    @abstractmethod
    def get_uptime(self) -> float:
        """Get the system uptime.
        
        Returns:
            float: Uptime in seconds
            
        Raises:
            HardwareError: If the uptime cannot be determined
        """
        pass

    @abstractmethod
    def get_memory_usage(self) -> MemoryUsage:
        """Get memory usage statistics.
        
        Returns:
            MemoryUsage: Memory usage information
            
        Raises:
            HardwareError: If memory usage cannot be determined
        """
        pass

    @abstractmethod
    def get_cpu_usage(self) -> float:
        """Get current CPU usage.
        
        Returns:
            float: CPU usage as a percentage (0-100)
            
        Raises:
            HardwareError: If CPU usage cannot be determined
        """
        pass

    @abstractmethod
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information.
        
        Returns:
            dict: Dictionary containing disk usage information
            
        Raises:
            HardwareError: If disk usage cannot be determined
        """
        pass

    @abstractmethod
    def get_boot_time(self) -> datetime:
        """Get the system boot time.
        
        Returns:
            datetime: System boot time
            
        Raises:
            HardwareError: If boot time cannot be determined
        """
        pass

    @abstractmethod
    def get_network_interfaces(self) -> Dict[str, Dict[str, Any]]:
        """Get information about network interfaces.
        
        Returns:
            dict: Dictionary of network interfaces and their status
            
        Raises:
            HardwareError: If network information cannot be retrieved
        """
        pass
