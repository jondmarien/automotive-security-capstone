"""Factory for creating and managing hardware components."""
from typing import Any, Dict, Optional, Type, TypeVar

from hardware.drivers.mock.rf import MockRFInterface
from hardware.drivers.mock.power import MockPowerInterface
from hardware.drivers.mock.status import MockStatusInterface
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
        """Initialize the hardware factory with default implementations."""
        if self._initialized:
            return
            
        self._components = {}
        
        # Register default implementations
        self._rf_impls = {
            'mock': MockRFInterface,
            # Add other implementations here
        }
        
        self._power_impls = {
            'default': MockPowerInterface,
            'mock': MockPowerInterface,
            # Add other implementations here
        }
        
        self._status_impls = {
            'default': MockStatusInterface,
            'mock': MockStatusInterface,
            # Add other implementations here
        }
        
        self._initialized = True
    
    async def _create_rf_interface(self, config: RFConfig, impl_name: str = 'mock') -> RFInterface:
        """Create an RF interface.
        
        Args:
            config: Configuration for the RF interface
            impl_name: Name of the implementation to use
            
        Returns:
            An initialized RF interface instance
            
        Note:
            This is an async method and should be awaited.
        """
        if 'RFInterface' not in self._components:
            # Get the implementation class
            impl_class = self._rf_impls.get(impl_name)
            if not impl_class:
                raise ValueError(f"No RF interface implementation found for '{impl_name}'")
                
            # Create the instance
            self._components['RFInterface'] = impl_class()
            
            # Initialize the interface if it has an initialize method
            if hasattr(self._components['RFInterface'], 'initialize'):
                # Ensure we have a complete config
                if config is None:
                    from hardware.models.models import RFConfig
                    config = RFConfig(
                        frequency=433.92e6,  # 433.92 MHz
                        power=10,            # 10 dBm
                        data_rate=100000,    # 100 kbps
                        modulation='FSK',    # FSK modulation
                        bandwidth=200000,    # 200 kHz
                        devitation=25000,    # 25 kHz
                        sync_word=b'\x12',   # Sync word
                        crc_enabled=True,    # Enable CRC
                        auto_ack=False,      # Disable auto-ack
                        node_id=1,           # Node ID
                        network_id=1         # Network ID
                    )
                await self._components['RFInterface'].initialize(config)
        return self._components['RFInterface']
    
    async def _create_power_interface(self) -> PowerInterface:
        """Create a power interface.
        
        Returns:
            An initialized power interface instance
            
        Note:
            This is an async method and should be awaited.
        """
        if 'PowerInterface' not in self._components:
            from hardware.drivers.mock.power import MockPowerInterface
            self._components['PowerInterface'] = MockPowerInterface()
            # Initialize the mock power interface
            if hasattr(self._components['PowerInterface'], 'initialize'):
                await self._components['PowerInterface'].initialize()
        return self._components['PowerInterface']
    
    async def create_rf_interface(self, 
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
            
        Note:
            This is an async method and should be awaited.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.debug(f"Creating RF interface with implementation: {impl_name}")
        impl_class = self._rf_impls.get(impl_name)
        if not impl_class:
            error_msg = f"No RF interface implementation found for '{impl_name}'"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        logger.debug(f"Found implementation class: {impl_class.__name__}")
        logger.debug(f"Using config: {config}")
        
        try:
            if config is None:
                logger.debug("No config provided, creating default config")
                from hardware.models.models import RFConfig
                config = RFConfig(
                    frequency=433.92e6,  # 433.92 MHz
                    power=10,            # 10 dBm
                    data_rate=100000,    # 100 kbps
                    modulation='FSK',    # FSK modulation
                    bandwidth=200000,    # 200 kHz
                    devitation=25000,    # 25 kHz
                    sync_word=b'\x12',   # Default sync word
                    crc_enabled=True,    # Enable CRC
                    auto_ack=False,      # Disable auto-ack
                    node_id=1,           # Default node ID
                    network_id=1         # Default network ID
                )
            
            logger.debug("Creating RF interface instance with config: %s", config)
            return await self._create_rf_interface(config, impl_name)
        except Exception as e:
            logger.exception("Error creating RF interface")
            raise
    
    async def create_power_manager(self, impl_name: str = 'default') -> PowerInterface:
        """Create a power manager.
        
        Args:
            impl_name: Name of the implementation to use
            
        Returns:
            PowerInterface: An instance of the requested power interface
            
        Raises:
            ValueError: If the implementation is not found
            
        Note:
            This is an async method and should be awaited.
        """
        impl_class = self._power_impls.get(impl_name)
        if not impl_class:
            raise ValueError(f"No power manager implementation found for '{impl_name}'")
            
        return await self._create_power_interface()
    
    async def _create_status_interface(self) -> StatusInterface:
        """Create and initialize a status interface.
        
        Returns:
            StatusInterface: An initialized status interface instance
            
        Note:
            This is an async method and should be awaited.
        """
        if 'StatusInterface' not in self._components:
            from hardware.drivers.mock.status import MockStatusInterface
            self._components['StatusInterface'] = MockStatusInterface()
            # Initialize the mock status interface
            if hasattr(self._components['StatusInterface'], 'initialize'):
                await self._components['StatusInterface'].initialize()
        return self._components['StatusInterface']
    
    async def create_status_interface(self, impl_name: str = 'default') -> StatusInterface:
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
            
        return self._create_status_interface()
    
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

