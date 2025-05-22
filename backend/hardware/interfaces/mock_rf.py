"""Mock implementation of the RF interface for testing."""
import asyncio
from typing import Any, Callable, Dict, Optional

from ..models.models import RFConfig, SignalMetrics
from .rf import RFInterface


class MockRFInterface(RFInterface):
    """Mock implementation of the RF interface for testing.
    
    This implementation simulates an RF interface in memory without requiring
    actual hardware. It's useful for testing and development.
    """
    
    def __init__(self):
        """Initialize the mock RF interface."""
        self._initialized = False
        self._receiving = False
        self._config: Optional[RFConfig] = None
        self._receive_callback: Optional[Callable[[bytes], None]] = None
        self._receive_task: Optional[asyncio.Task] = None
        self._packet_queue: asyncio.Queue[bytes] = asyncio.Queue()
        
    async def initialize(self, config: RFConfig) -> None:
        """Initialize the mock RF interface with the given configuration."""
        if self._initialized:
            raise RuntimeError("RF interface already initialized")
            
        self._config = config
        self._initialized = True
        
    async def start_receiving(self, callback: Callable[[bytes], None]) -> None:
        """Start receiving packets with the given callback."""
        if not self._initialized:
            raise RuntimeError("RF interface not initialized")
            
        if self._receiving:
            raise RuntimeError("Already receiving")
            
        self._receive_callback = callback
        self._receiving = True
        self._receive_task = asyncio.create_task(self._receive_loop())
        
    async def stop_receiving(self) -> None:
        """Stop receiving packets."""
        if not self._receiving or not self._receive_task:
            return
            
        self._receiving = False
        self._receive_task.cancel()
        try:
            await self._receive_task
        except asyncio.CancelledError:
            pass
        finally:
            self._receive_task = None
            self._receive_callback = None
    
    async def _receive_loop(self) -> None:
        """Background task that processes received packets."""
        while self._receiving and self._receive_callback:
            try:
                # Process any queued packets
                while not self._packet_queue.empty():
                    packet = await asyncio.wait_for(
                        self._packet_queue.get(),
                        timeout=0.1
                    )
                    if self._receive_callback:
                        try:
                            # Ensure the callback is awaited if it's a coroutine
                            if asyncio.iscoroutinefunction(self._receive_callback):
                                await self._receive_callback(packet)
                            else:
                                # If it's a regular function, run it in the event loop
                                loop = asyncio.get_running_loop()
                                await loop.run_in_executor(None, self._receive_callback, packet)
                        except Exception as e:
                            print(f"Error in receive callback: {e}")
                
                # Small sleep to prevent busy-waiting
                await asyncio.sleep(0.01)
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in receive loop: {e}")
                break
    
    async def send_packet(self, data: bytes, timeout: float = 5.0) -> bool:
        """Send a packet."""
        if not self._initialized:
            raise RuntimeError("RF interface not initialized")
            
        if not isinstance(data, bytes):
            raise ValueError("Data must be bytes")
            
        # In a real implementation, this would transmit the packet over RF
        # For the mock, we'll just queue it for reception
        if self._receiving and self._receive_callback:
            await self._packet_queue.put(data)
            
        return True
    
    def get_signal_metrics(self) -> Dict[str, Any]:
        """Get current signal metrics."""
        if not self._initialized:
            raise RuntimeError("RF interface not initialized")
            
        # Return mock signal metrics
        return SignalMetrics(
            rssi=-60.0,  # Typical good signal
            snr=25.0,    # Good SNR
            frequency=self._config.frequency if self._config else 0,
            channel=1    # Default channel
        ).__dict__
    
    @property
    def is_initialized(self) -> bool:
        """Check if the interface is initialized."""
        return self._initialized
    
    @property
    def is_receiving(self) -> bool:
        """Check if the interface is currently receiving."""
        return self._receiving and self._initialized
