"""Mock implementation of the status interface for testing."""
import asyncio
import logging
import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from hardware.exceptions.exceptions import HardwareError
from hardware.interfaces.status import StatusInterface
from hardware.models.models import MemoryUsage

logger = logging.getLogger(__name__)

class MockStatusInterface(StatusInterface):
    """Mock implementation of the StatusInterface for testing."""

    def __init__(self):
        """Initialize the mock status interface."""
        self._initialized = False
        self._start_time = datetime.now(timezone.utc)
        self._boot_time = datetime.now(timezone.utc) - timedelta(hours=1)
        self._temperature = 42.0  # Default temperature in Celsius
        self._memory_usage = MemoryUsage(
            total=1024 * 1024 * 1024,  # 1GB
            used=512 * 1024 * 1024,    # 512MB
            free=512 * 1024 * 1024,    # 512MB
            usage_percent=50.0
        )
        self._cpu_usage = 25.0  # 25% CPU usage
        self._disk_usage = {
            'total': 32 * 1024 * 1024 * 1024,  # 32GB
            'used': 16 * 1024 * 1024 * 1024,  # 16GB
            'free': 16 * 1024 * 1024 * 1024,  # 16GB
            'percent': 50.0
        }
        self._network_interfaces = {
            'eth0': {
                'ip_address': '192.168.1.100',
                'mac_address': '00:11:22:33:44:55',
                'is_up': True,
                'bytes_sent': 1024 * 1024,
                'bytes_recv': 2 * 1024 * 1024
            },
            'wlan0': {
                'ip_address': '192.168.1.101',
                'mac_address': '00:11:22:33:44:56',
                'is_up': True,
                'bytes_sent': 512 * 1024,
                'bytes_recv': 1024 * 1024
            }
        }
        
    async def initialize(self) -> None:
        """Initialize the mock status interface."""
        self._initialized = True
        logger.info("Mock status interface initialized")
        self._start_time = datetime.now(timezone.utc)
        
    def get_temperature(self) -> float:
        """Get the current temperature in Celsius."""
        if not self._initialized:
            raise HardwareError("Status interface not initialized")
            
        # Add some random variation to the temperature
        self._temperature = max(0, min(85, self._temperature + (random.random() - 0.5) * 2))
        return self._temperature
        
    def get_uptime(self) -> float:
        """Get the system uptime in seconds."""
        if not self._initialized:
            raise HardwareError("Status interface not initialized")
            
        return (datetime.now(timezone.utc) - self._boot_time).total_seconds()
        
    def get_memory_usage(self) -> MemoryUsage:
        """Get current memory usage.
        
        Returns:
            MemoryUsage: Memory usage information
            
        Raises:
            HardwareError: If memory usage cannot be determined
        """
        if not self._initialized:
            raise HardwareError("Status interface not initialized")
            
        # Add some random variation to memory usage
        used = self._memory_usage.used + (random.randint(-100, 100) * 1024 * 1024)
        used = max(0, min(used, self._memory_usage.total))
        free = self._memory_usage.total - used
        usage_percent = (used / self._memory_usage.total) * 100
        
        return MemoryUsage(
            total=self._memory_usage.total,
            used=used,
            free=free,
            usage_percent=usage_percent
        )
        
    def get_cpu_usage(self) -> float:
        """Get current CPU usage.
        
        Returns:
            float: CPU usage as a percentage (0-100)
            
        Raises:
            HardwareError: If CPU usage cannot be determined
        """
        if not self._initialized:
            raise HardwareError("Status interface not initialized")
            
        # Add some random variation to CPU usage
        self._cpu_usage = max(0, min(100, self._cpu_usage + (random.random() - 0.5) * 10))
        return self._cpu_usage
        
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information.
        
        Returns:
            dict: Dictionary containing disk usage information
            
        Raises:
            HardwareError: If disk usage cannot be determined
        """
        if not self._initialized:
            raise HardwareError("Status interface not initialized")
            
        # Add some random variation to disk usage
        used = self._disk_usage['used'] + (random.randint(-100, 100) * 1024 * 1024)
        used = max(0, min(used, self._disk_usage['total']))
        self._disk_usage['used'] = used
        self._disk_usage['free'] = self._disk_usage['total'] - used
        self._disk_usage['percent'] = (used / self._disk_usage['total']) * 100
        
        return {
            'total': self._disk_usage['total'],
            'used': used,
            'free': self._disk_usage['free'],
            'percent': self._disk_usage['percent']
        }
        
    def get_boot_time(self) -> datetime:
        """Get the system boot time.
        
        Returns:
            datetime: System boot time
            
        Raises:
            HardwareError: If boot time cannot be determined
        """
        if not self._initialized:
            raise HardwareError("Status interface not initialized")
            
        return self._boot_time
        
    def get_network_interfaces(self) -> Dict[str, Dict[str, Any]]:
        """Get information about network interfaces.
        
        Returns:
            dict: Dictionary of network interfaces and their status
            
        Raises:
            HardwareError: If network information cannot be retrieved
        """
        if not self._initialized:
            raise HardwareError("Status interface not initialized")
            
        # Update network statistics with some random variation
        for iface in self._network_interfaces.values():
            iface['bytes_sent'] += random.randint(0, 1000)
            iface['bytes_recv'] += random.randint(0, 1000)
            
        return self._network_interfaces.copy()
    
    async def shutdown(self) -> None:
        """Shut down the status interface."""
        self._initialized = False
        logger.info("Mock status interface shut down")
