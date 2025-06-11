"""
packet.py

Defines a minimal Packet class for use in security analysis and reporting.
"""
from typing import Optional

class Packet:
    """
    Represents a captured RF or NFC packet/event for analysis.
    """
    def __init__(self, payload: bytes, freq: float, rssi: float, snr: Optional[float]=None, tag_id: Optional[str]=None):
        self.payload = payload
        self.freq = freq
        self.rssi = rssi
        self.snr = snr
        self.tag_id = tag_id
        self.timestamp = None  # Set by analyzer when processed

    def to_dict(self):
        return {
            'payload': self.payload.decode(errors='replace') if isinstance(self.payload, bytes) else str(self.payload),
            'freq': self.freq,
            'rssi': self.rssi,
            'snr': self.snr,
            'tag_id': self.tag_id,
            'timestamp': self.timestamp
        }
