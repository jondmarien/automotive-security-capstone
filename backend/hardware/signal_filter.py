"""Signal filtering and analysis for automotive security."""

import time
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from .packet import Packet  # noqa: F401

# Constants
MIN_RSSI_DBM = -90  # Minimum signal strength in dBm
DUP_WINDOW_SEC = 5  # Time window for duplicate detection in seconds
MAX_DUPES = 5  # Maximum number of duplicate packets allowed in the window

# Frequency bands to monitor (MHz)
FREQ_BANDS = [
    (2400, 2483.5),  # 2.4 GHz ISM band
    (5150, 5850),    # 5 GHz band
    (5725, 5875),    # 5.8 GHz band
    (315, 350),      # Lower ISM band
    (433, 434),      # 433 MHz ISM band
    (868, 928),      # 915 MHz ISM band (North America)
]

class SignalFilter:
    """Processes and filters RF signals for potential security threats."""
    
    def __init__(self, min_rssi: int = MIN_RSSI_DBM, 
                 duplicate_window: float = DUP_WINDOW_SEC,
                 max_duplicates: int = MAX_DUPES):
        """Initialize signal filter with configuration."""
        self.min_rssi = min_rssi
        self.duplicate_window_sec = duplicate_window
        self.max_duplicates = max_duplicates
        self.packet_history = {}  # signature -> list of timestamps
        self.last_seen = {}  # signature -> last seen timestamp
        self.freq_bands = FREQ_BANDS  # Store frequency bands
        self.active_signals = 0
    
    def is_within_freq_bands(self, freq: float) -> bool:
        """Check if frequency is within monitored bands."""
        if not isinstance(freq, (int, float)):
            return False
        return any(lower <= freq <= upper for lower, upper in self.freq_bands)
    
    def is_strong_signal(self, rssi: int) -> bool:
        """Check if signal strength is above minimum threshold."""
        if not isinstance(rssi, (int, float)):
            return False
        return rssi >= self.min_rssi
    
    def is_duplicate(self, signature: str, timestamp: float, threshold: int = 1) -> bool:
        """Check if a packet with the same signature was seen recently.
        
        Args:
            signature: The packet signature to check
            timestamp: The current timestamp
            threshold: Number of previous occurrences before considering it a duplicate
                     (1 = mark as duplicate on second occurrence, 2 = on third, etc.)
        """
        if not signature or not isinstance(timestamp, (int, float)):
            return False
            
        # Initialize packet history for this signature if it doesn't exist
        if signature not in self.packet_history:
            self.packet_history[signature] = []
            
        # Clean up old entries for this signature
        previous_timestamps = [
            ts for ts in self.packet_history[signature]
            if timestamp - ts <= self.duplicate_window_sec
        ]
        
        # Check if we've seen this packet enough times to be considered a duplicate
        is_duplicate = len(previous_timestamps) >= threshold
        
        # Add current timestamp to history (even if it's a duplicate timestamp)
        previous_timestamps.append(timestamp)
        
        # Update the packet history with cleaned timestamps
        self.packet_history[signature] = previous_timestamps
        self.last_seen[signature] = timestamp
        
        # Check if we've exceeded max duplicates for this signature
        if len(self.packet_history[signature]) > self.max_duplicates:
            return True
            
        return is_duplicate

    def should_accept(self, packet: 'Packet') -> bool:
        """Determine if a packet should be accepted based on all criteria."""
        if not self.is_within_freq_bands(packet.freq):
            return False
        if not self.is_strong_signal(packet.rssi):
            return False
        if self.is_duplicate(packet.signature, packet.timestamp, threshold=2):
            return False
            
        self.active_signals += 1
        return True
    
    def get_signal_metrics(self) -> dict:
        """Get current signal metrics."""
        # Clean up old entries before reporting metrics
        current_time = time.time()
        
        for sig in list(self.packet_history.keys()):
            self.packet_history[sig] = [
                ts for ts in self.packet_history[sig]
                if current_time - ts <= self.duplicate_window_sec
            ]
            if not self.packet_history[sig]:
                del self.packet_history[sig]
                self.last_seen.pop(sig, None)
        
        return {
            'active_signals': self.active_signals,
            'min_rssi': self.min_rssi,
            'monitored_bands': self.freq_bands,
            'duplicate_window_sec': self.duplicate_window_sec,
            'max_duplicates': self.max_duplicates
        }
