"""Factory for creating hardware components."""
from typing import Any, Dict, Optional, Type

from .implementations.mock_rf import MockRF
from .interfaces.power import PowerManager
from .interfaces.rf import RFInterface
from .interfaces.status import HardwareStatus
from .models import RFConfig


class HardwareFactory:
    """Factory for creating hardware components."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Create a singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the factory."""
        if not self._initialized:
            self._rf_impls = {
                'mock': MockRF,
                # Add other implementations here (e.g., 'cc1101', 'sdr')
            }
            self._power_impls = {
                # Add power management implementations here
            }
            self._status_impls = {
                # Add status monitoring implementations here
            }
            self._initialized = True
    
    def create_rf_interface(self, 
                           impl_name: str = 'mock',
                           config: Optional[RFConfig] = None) -> RFInterface:
        """Create an RF interface.
        
        Args:
            impl_name: Name of the implementation to use
            config: Configuration for the RF interface
            
        Returns:
            RFInterface: An instance of the requested RF interface
            
        Raises:
            ValueError: If the implementation is not found
        """
        impl_class = self._rf_impls.get(impl_name.lower())
        if not impl_class:
            raise ValueError(f"No RF implementation found for '{impl_name}'")
            
        return impl_class()
    
    def create_power_manager(self, impl_name: str = 'default') -> PowerManager:
        """Create a power manager.
        
        Args:
            impl_name: Name of the implementation to use
            
        Returns:
            PowerManager: An instance of the requested power manager
            
        Raises:
            ValueError: If the implementation is not found
        """
        impl_class = self._power_impls.get(impl_name.lower())
        if not impl_class:
            raise ValueError(f"No power manager implementation found for '{impl_name}'")
            
        return impl_class()
    
    def create_hardware_status(self, impl_name: str = 'default') -> HardwareStatus:
        """Create a hardware status monitor.
        
        Args:
            impl_name: Name of the implementation to use
            
        Returns:
            HardwareStatus: An instance of the requested hardware status monitor
            
        Raises:
            ValueError: If the implementation is not found
        """
        impl_class = self._status_impls.get(impl_name.lower())
        if not impl_class:
            raise ValueError(f"No hardware status implementation found for '{impl_name}'")
            
        return impl_class()
    
    def register_rf_implementation(self, name: str, impl_class: Type[RFInterface]) -> None:
        """Register a custom RF interface implementation.
        
        Args:
            name: Name to register the implementation under
            impl_class: The implementation class (must be a subclass of RFInterface)
            
        Raises:
            TypeError: If impl_class is not a subclass of RFInterface
        """
        if not issubclass(impl_class, RFInterface):
            raise TypeError("RF implementation must be a subclass of RFInterface")
        self._rf_impls[name.lower()] = impl_class
    
    def register_power_implementation(self, name: str, impl_class: Type[PowerManager]) -> None:
        """Register a custom power manager implementation.
        
        Args:
            name: Name to register the implementation under
            impl_class: The implementation class (must be a subclass of PowerManager)
            
        Raises:
            TypeError: If impl_class is not a subclass of PowerManager
        """
        if not issubclass(impl_class, PowerManager):
            raise TypeError("Power manager implementation must be a subclass of PowerManager")
        self._power_impls[name.lower()] = impl_class
    
    def register_status_implementation(self, name: str, impl_class: Type[HardwareStatus]) -> None:
        """Register a custom hardware status implementation.
        
        Args:
            name: Name to register the implementation under
            impl_class: The implementation class (must be a subclass of HardwareStatus)
            
        Raises:
            TypeError: If impl_class is not a subclass of HardwareStatus
        """
        if not issubclass(impl_class, HardwareStatus):
            raise TypeError("Hardware status implementation must be a subclass of HardwareStatus")
        self._status_impls[name.lower()] = impl_class


# Create a singleton instance
hardware_factory = HardwareFactory()
