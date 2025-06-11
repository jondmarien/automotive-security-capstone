"""
mock/rf.py

Mock RF interface for generating plausible RF signal metrics and packet payloads.
"""
import random
from typing import Optional

class MockRFInterface:
    """
    Simulates an RF transceiver for dashboard mock/demo mode.
    """
    def __init__(self):
        self.frequency = 434e6
        self.power = 14
        self.data_rate = 50000
        self.modulation = 'FSK'
        self.bandwidth = 125e3
        self.devitation = 50e3
        self.initialized = True

    def get_signal_metrics(self):
        """
        Return plausible RF metrics.
        """
        # Simulate plausible RF metrics with some variation
        return {
            'rssi': random.gauss(-55, 8),  # dBm, centered at -55
            'snr': random.gauss(20, 5),    # dB, centered at 20
            'frequency': self.frequency,
            'channel': 1,
        }

    def get_packet(self):
        """
        Simulate receiving a packet with plausible payload and metrics.
        """
        payloads = [b'UNLOCK', b'LOCK', b'NFC_SCAN', b'REPLAY_ATTACK', b'JAMMER', b'BRUTE', b'NORMAL']
        payload = random.choice(payloads)
        metrics = self.get_signal_metrics()
        return {
            'payload': payload,
            'freq': metrics['frequency'],
            'rssi': metrics['rssi'],
            'snr': metrics['snr'],
        }
