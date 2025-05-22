"""Hardware abstraction layer interfaces."""
# Import interfaces
from .power import PowerInterface
from .rf import RFInterface
from .status import StatusInterface

# Import mock implementations conditionally to avoid circular imports
if 'sphinx' not in __import__('sys').modules[__name__].__package__:
    from hardware.drivers.mock.rf import MockRFInterface
    __all__ = [
        'RFInterface',
        'MockRFInterface',
        'PowerInterface',
        'StatusInterface'
    ]
else:
    __all__ = [
        'RFInterface',
        'PowerInterface',
        'StatusInterface'
    ]
