"""
mock/nfc.py

Mock NFC interface for generating plausible NFC scan/tag events.
"""

import random


class MockNFCInterface:
    """
    Simulates an NFC reader for dashboard mock/demo mode.
    """

    def __init__(self):
        self.initialized = True

    def get_nfc_data(self):
        """
        Return plausible NFC scan/tag data.
        """
        tag_ids = [None, "TAG123", "TAG999", "TAGABC"]
        tag_id = random.choices(tag_ids, weights=[0.7, 0.1, 0.1, 0.1])[0]
        return {"nfc_anomaly": bool(tag_id and random.random() < 0.2), "tag_id": tag_id}
