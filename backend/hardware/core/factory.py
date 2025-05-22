"""Factory for creating and managing hardware components."""
from typing import Any, Dict, Optional, Type, TypeVar

from hardware.drivers.mock.rf import MockRFInterface
from hardware.interfaces.power import PowerInterface
from hardware.interfaces.rf import RFInterface
from hardware.interfaces.status import StatusInterface
from hardware.models.models import RFConfig

T = TypeVar('T')

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
                'mock': MockRFInterface,
                # Add other implementations here (e.g., 'cc1101', 'sdr')
            }
            self._power_impls = {
                # Add power management implementations here
            }
            self._status_impls = {
                # Add status monitoring implementations here
            }
            self._components = {}
            self._initialized = True
    
    def _create_rf_interface(self, config: RFConfig) -> RFInterface:
        """Create an RF interface.
        
        Args:
            config: Configuration for the RF interface
            
        Returns:
            An initialized RF interface instance
        """
        if 'RFInterface' not in self._components:
            # In a real implementation, this would create the appropriate RF interface
            # based on the configuration. For now, we'll just use the mock implementation.
            self._components['RFInterface'] = MockRFInterface()
            self._components['RFInterface'].initialize(config)
        return self._components['RFInterface']
    
    def _create_power_interface(self) -> PowerInterface:
        """Create a power interface.
        
        Returns:
            An initialized power interface instance
        """
        # In a real implementation, this would create the appropriate power interface
        # based on the configuration. For now, we'll just use a default implementation.
        if 'PowerInterface' not in self._components:
            self._components['PowerInterface'] = PowerInterface()
        return self._components['PowerInterface']
    
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
            
        return self._create_rf_interface(config)
    
    def create_power_manager(self, impl_name: str = 'default') -> PowerInterface:
        """Create a power manager.
        
        Args:
            impl_name: Name of the implementation to use
            
        Returns:
            PowerInterface: An instance of the requested power interface
            
        Raises:
            ValueError: If the implementation is not found
        """
        impl_class = self._power_impls.get(impl_name.lower())
        if not impl_class:
            raise ValueError(f"No power manager implementation found for '{impl_name}'")
            
        return self._create_power_interface()
    
    def create_status_interface(self, impl_name: str = 'default') -> StatusInterface:
        """Create a status interface.
        
        Args:
            impl_name: Name of the implementation to use
            
        Returns:
            StatusInterface: An instance of the requested status interface
            
        Raises:
            ValueError: If the implementation is not found
        """
        impl_class = self._status_impls.get(impl_name.lower())
        if not impl_class:
            raise ValueError(f"No status interface implementation found for '{impl_name}'")
            
        if 'StatusInterface' not in self._components:
            self._components['StatusInterface'] = impl_class()
        return self._components['StatusInterface']
    
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
    
    def register_power_implementation(self, name: str, impl_class: Type[PowerInterface]) -> None:
        """Register a custom power manager implementation.
        
        Args:
            name: Name to register the implementation under
            impl_class: The implementation class (must be a subclass of PowerInterface)
            
        Raises:
            TypeError: If impl_class is not a subclass of PowerInterface
        """
        if not issubclass(impl_class, PowerInterface):
            raise TypeError("Power manager implementation must be a subclass of PowerInterface")
        self._power_impls[name.lower()] = impl_class
    
    def register_status_implementation(self, name: str, impl_class: Type[StatusInterface]) -> None:
        """Register a custom hardware status implementation.
        
        Args:
            name: Name to register the implementation under
            impl_class: The implementation class (must be a subclass of StatusInterface)
            
        Raises:
            TypeError: If impl_class is not a subclass of StatusInterface
        """
        if not issubclass(impl_class, StatusInterface):
            raise TypeError("Hardware status implementation must be a subclass of StatusInterface")
        self._status_impls[name.lower()] = impl_class


# Create a singleton instance
hardware_factory = HardwareFactory()

