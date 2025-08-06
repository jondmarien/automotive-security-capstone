"""
Test suite for event logic module.

Tests comprehensive event analysis functionality including:
- Demo mode event assignment
- Real packet analysis logic
- Threat level assignment
- Color mapping
- Event type classification
"""

from unittest.mock import patch, MagicMock

from detection.event_logic import analyze_event, THREAT_COLOR_MAP, ALL_EVENT_TYPES, DETAILS_MAP


class TestEventLogic:
    """Test cases for event logic functions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sample_packet = {
            "timestamp": "2025-08-06 08:00:00",
            "frequency": 433.92e6,
            "rssi": -50.0,
            "data": b'\x01\x02\x03\x04'
        }

    def test_analyze_event_demo_mode_replay_attack(self):
        """Test analyze_event in demo mode with replay attack."""
        packet = {
            **self.sample_packet,
            "event_type": "Replay Attack"
        }
        
        result = analyze_event(packet, demo_mode=True)
        
        assert result["event_type"] == "Replay Attack"
        assert result["threat_level"] == "Malicious"
        assert result["color"] == "red"
        assert result["timestamp"] == packet["timestamp"]
        assert "desc" in result["details"]
        assert result["frequency"] == packet["frequency"]
        assert result["rssi"] == packet["rssi"]

    def test_analyze_event_demo_mode_unknown(self):
        """Test analyze_event in demo mode with unknown event."""
        packet = {
            **self.sample_packet,
            "event_type": "Unknown"
        }
        
        result = analyze_event(packet, demo_mode=True)
        
        assert result["event_type"] == "Unknown"
        assert result["threat_level"] == "Suspicious"
        assert result["color"] == "orange"

    def test_analyze_event_demo_mode_jamming_attack(self):
        """Test analyze_event in demo mode with jamming attack."""
        packet = {
            **self.sample_packet,
            "event_type": "Jamming Attack"
        }
        
        result = analyze_event(packet, demo_mode=True)
        
        assert result["event_type"] == "Jamming Attack"
        assert result["threat_level"] == "Malicious"
        assert result["color"] == "red"

    def test_analyze_event_demo_mode_brute_force(self):
        """Test analyze_event in demo mode with brute force."""
        packet = {
            **self.sample_packet,
            "event_type": "Brute Force"
        }
        
        result = analyze_event(packet, demo_mode=True)
        
        assert result["event_type"] == "Brute Force"
        assert result["threat_level"] == "Malicious"
        assert result["color"] == "red"

    def test_analyze_event_demo_mode_rf_unlock(self):
        """Test analyze_event in demo mode with RF unlock."""
        packet = {
            **self.sample_packet,
            "event_type": "RF Unlock"
        }
        
        result = analyze_event(packet, demo_mode=True)
        
        assert result["event_type"] == "RF Unlock"
        assert result["threat_level"] == "Benign"
        assert result["color"] == "green"

    def test_analyze_event_demo_mode_rf_lock(self):
        """Test analyze_event in demo mode with RF lock."""
        packet = {
            **self.sample_packet,
            "event_type": "RF Lock"
        }
        
        result = analyze_event(packet, demo_mode=True)
        
        assert result["event_type"] == "RF Lock"
        assert result["threat_level"] == "Benign"
        assert result["color"] == "green"

    def test_analyze_event_demo_mode_nfc_scan(self):
        """Test demo mode event analysis for NFC scan."""
        packet = {"event_type": "NFC Scan"}
        
        # In demo mode, the function uses random.choice, so we need to patch it
        with patch('detection.event_logic.random.choice') as mock_choice:
            mock_choice.return_value = "NFC Scan"
            
            result = analyze_event(packet, demo_mode=True)
        
        assert result["event_type"] == "NFC Scan"
        assert result["threat_level"] == "Benign"
        assert result["color"] == "green"

    def test_analyze_event_demo_mode_nfc_tag_present(self):
        """Test demo mode event analysis for NFC tag present."""
        packet = {"event_type": "NFC Tag Present"}
        
        # In demo mode, the function uses random.choice, so we need to patch it
        with patch('detection.event_logic.random.choice') as mock_choice:
            mock_choice.return_value = "NFC Tag Present"
            
            result = analyze_event(packet, demo_mode=True)
        
        assert result["event_type"] == "NFC Tag Present"
        assert result["threat_level"] == "Benign"
        assert result["color"] == "green"

    @patch('random.choice')
    def test_analyze_event_demo_mode_random_event_type(self, mock_choice):
        """Test analyze_event in demo mode with random event type selection."""
        mock_choice.return_value = "RF Unlock"
        
        packet = {
            **self.sample_packet,
            # No event_type specified
        }
        
        result = analyze_event(packet, demo_mode=True)
        
        assert result["event_type"] == "RF Unlock"
        mock_choice.assert_called_once_with(ALL_EVENT_TYPES)

    @patch('random.choice')
    def test_analyze_event_demo_mode_invalid_event_type(self, mock_choice):
        """Test analyze_event in demo mode with invalid event type."""
        mock_choice.return_value = "Jamming Attack"
        
        packet = {
            **self.sample_packet,
            "event_type": "Invalid Event Type"
        }
        
        result = analyze_event(packet, demo_mode=True)
        
        assert result["event_type"] == "Jamming Attack"
        mock_choice.assert_called_once_with(ALL_EVENT_TYPES)

    @patch('detection.event_logic.random.choices')
    def test_analyze_event_demo_mode_ambiguous_event(self, mock_choices):
        """Test demo mode with ambiguous event type."""
        packet = {"event_type": "Other"}
        
        # Mock random.choices to return a specific threat level
        mock_choices.return_value = ["Suspicious"]
        
        # In demo mode, the function uses random.choice, so we need to patch it
        with patch('detection.event_logic.random.choice') as mock_choice:
            mock_choice.return_value = "Other"
            
            result = analyze_event(packet, demo_mode=True)
        
        assert result["event_type"] == "Other"
        assert result["threat_level"] == "Suspicious"
        assert result["color"] == "orange"  # Suspicious -> orange
        mock_choices.assert_called_once_with(
            ["Benign", "Suspicious", "Malicious"], 
            weights=[1, 2, 4], 
            k=1
        )

    def test_analyze_event_demo_mode_default_benign(self):
        """Test demo mode with default benign event."""
        packet = {"custom_field": "test"}
        
        # In demo mode, the function uses random.choice, so we need to patch it
        with patch('detection.event_logic.random.choice') as mock_choice:
            mock_choice.return_value = "Some Other Event"
            
            result = analyze_event(packet, demo_mode=True)
        
        assert result["event_type"] == "Some Other Event"
        assert result["threat_level"] == "Benign"
        assert result["color"] == "green"

    @patch('detection.event_logic.datetime')
    def test_analyze_event_demo_mode_missing_timestamp(self, mock_datetime):
        """Test analyze_event in demo mode with missing timestamp."""
        mock_now = MagicMock()
        mock_now.strftime.return_value = "2025-08-06 12:00:00"
        mock_datetime.now.return_value = mock_now
        
        packet = {
            "event_type": "RF Unlock",
            "frequency": 433.92e6
        }
        
        result = analyze_event(packet, demo_mode=True)
        
        assert result["timestamp"] == "2025-08-06 12:00:00"
        mock_datetime.now.assert_called_once()

    def test_analyze_event_real_mode_replay_attack(self):
        """Test analyze_event in real mode with replay attack detection."""
        packet = {
            **self.sample_packet,
            "is_replay": True
        }
        
        result = analyze_event(packet, demo_mode=False)
        
        assert result["event_type"] == "Replay Attack"
        assert result["threat_level"] == "Malicious"
        assert result["color"] == "red"

    def test_analyze_event_real_mode_jamming_attack(self):
        """Test analyze_event in real mode with jamming attack detection."""
        packet = {
            **self.sample_packet,
            "is_jamming": True
        }
        
        result = analyze_event(packet, demo_mode=False)
        
        assert result["event_type"] == "Jamming Attack"
        assert result["threat_level"] == "Malicious"
        assert result["color"] == "red"

    def test_analyze_event_real_mode_brute_force(self):
        """Test analyze_event in real mode with brute force detection."""
        packet = {
            **self.sample_packet,
            "is_brute": True
        }
        
        result = analyze_event(packet, demo_mode=False)
        
        # In real mode, Brute Force is always Malicious regardless of RSSI
        assert result["event_type"] == "Brute Force"
        assert result["threat_level"] == "Malicious"  # Brute Force -> Malicious
        assert result["color"] == "red"

    def test_analyze_event_real_mode_rf_lock(self):
        """Test analyze_event in real mode with RF lock."""
        packet = {
            **self.sample_packet,
            "is_lock": True,
            "rssi": -40  # High RSSI for Benign threat level
        }
        
        result = analyze_event(packet, demo_mode=False)
        
        assert result["event_type"] == "RF Lock"
        assert result["threat_level"] == "Benign"
        assert result["color"] == "green"

    def test_analyze_event_real_mode_unknown_strong_signal(self):
        """Test analyze_event in real mode with unknown but strong signal."""
        packet = {
            **self.sample_packet,
            "rssi": -40.0  # Strong signal
        }
        
        result = analyze_event(packet, demo_mode=False)
        
        # Unknown events are always Suspicious regardless of RSSI
        assert result["event_type"] == "Unknown"
        assert result["threat_level"] == "Suspicious"  # Unknown -> Suspicious
        assert result["color"] == "orange"

    def test_analyze_event_real_mode_unknown_weak_signal(self):
        """Test analyze_event in real mode with unknown weak signal."""
        packet = {
            **self.sample_packet,
            "rssi": -70.0  # Weak signal
        }
        
        result = analyze_event(packet, demo_mode=False)
        
        assert result["event_type"] == "Unknown"
        assert result["threat_level"] == "Suspicious"  # Weak signal is Suspicious
        assert result["color"] == "orange"

    def test_analyze_event_real_mode_existing_event_type(self):
        """Test analyze_event in real mode with existing event type."""
        packet = {
            **self.sample_packet,
            "event_type": "RF Unlock",
            "rssi": -40  # High RSSI for Benign threat level
        }
        
        result = analyze_event(packet, demo_mode=False)
        
        assert result["event_type"] == "RF Unlock"
        assert result["threat_level"] == "Benign"
        assert result["color"] == "green"

    def test_analyze_event_real_mode_rssi_based_threat_assessment(self):
        """Test analyze_event real mode RSSI-based threat assessment."""
        # Strong signal - benign
        packet_strong = {
            **self.sample_packet,
            "rssi": -40.0,
            "is_unlock": True
        }
        
        result_strong = analyze_event(packet_strong, demo_mode=False)
        assert result_strong["threat_level"] == "Benign"
        
        # Weak signal - suspicious
        packet_weak = {
            **self.sample_packet,
            "rssi": -70.0,
            "is_unlock": True
        }
        
        result_weak = analyze_event(packet_weak, demo_mode=False)
        assert result_weak["threat_level"] == "Suspicious"

    def test_analyze_event_field_passthrough(self):
        """Test that custom fields are passed through in the result."""
        packet = {
            **self.sample_packet,
            "custom_field": "custom_value",
            "another_field": 123,
            "rssi": -40  # High RSSI for Benign threat level
        }
        
        result = analyze_event(packet, demo_mode=False)
        
        assert result["custom_field"] == "custom_value"
        assert result["another_field"] == 123
        # Unknown events are always Suspicious regardless of RSSI
        assert result["threat_level"] == "Suspicious"
        assert result["color"] == "orange"

    def test_analyze_event_field_exclusion(self):
        """Test that reserved fields are not duplicated in passthrough."""
        packet = {
            **self.sample_packet,
            "event_type": "Custom Event",
            "threat_level": "Custom Threat",
            "color": "custom_color",
            "timestamp": "custom_timestamp",
            "details": "custom_details",
            "rssi": -40  # High RSSI for Benign threat level
        }
        
        result = analyze_event(packet, demo_mode=False)
        
        # Reserved fields should be overridden by function logic
        assert result["event_type"] == "Unknown"  # No matching flags
        # Unknown events are always Suspicious regardless of RSSI
        assert result["threat_level"] == "Suspicious"
        assert result["color"] == "orange"
        assert "timestamp" in result
        # Details should come from DETAILS_MAP for "Unknown" event type
        assert "desc" in result["details"]  # Unknown event has details
        assert "Malicious" in THREAT_COLOR_MAP
        
        assert THREAT_COLOR_MAP["Benign"] == "green"
        assert THREAT_COLOR_MAP["Suspicious"] == "orange"
        assert THREAT_COLOR_MAP["Malicious"] == "red"

    def test_details_map_coverage(self):
        """Test that DETAILS_MAP covers expected event types."""
        expected_events = [
            "RF Unlock", "RF Lock", "Replay Attack", 
            "Jamming Attack", "Brute Force", "Unknown"
        ]
        
        for event_type in expected_events:
            assert event_type in DETAILS_MAP
            assert "desc" in DETAILS_MAP[event_type]
            assert "example" in DETAILS_MAP[event_type]

    def test_all_event_types_from_details_map(self):
        """Test that ALL_EVENT_TYPES matches DETAILS_MAP keys."""
        assert set(ALL_EVENT_TYPES) == set(DETAILS_MAP.keys())

    def test_analyze_event_missing_details_fallback(self):
        """Test analyze_event with event type not in details map."""
        packet = {
            **self.sample_packet,
            "event_type": "Nonexistent Event"
        }
        
        result = analyze_event(
            packet, 
            demo_mode=False, 
            event_types=["Nonexistent Event"]
        )
        
        assert result["event_type"] == "Nonexistent Event"
        assert result["details"] == {}  # Empty dict fallback

    def test_analyze_event_color_fallback(self):
        """Test analyze_event with unknown threat level."""
        # This is a bit contrived since we control threat level assignment,
        # but tests the fallback mechanism
        packet = {
            **self.sample_packet,
            "event_type": "RF Unlock"
        }
        
        # Temporarily modify THREAT_COLOR_MAP to test fallback
        original_map = THREAT_COLOR_MAP.copy()
        THREAT_COLOR_MAP.clear()
        
        try:
            result = analyze_event(packet, demo_mode=False)
            assert result["color"] == "white"  # Fallback color
        finally:
            THREAT_COLOR_MAP.update(original_map)

    def test_analyze_event_multiple_flags(self):
        """Test analyze_event with multiple detection flags."""
        packet = {
            **self.sample_packet,
            "is_replay": True,
            "is_jamming": True,  # Should be ignored, replay takes precedence
            "is_brute": True     # Should be ignored
        }
        
        result = analyze_event(packet, demo_mode=False)
        
        # Replay should take precedence based on the if-elif chain
        assert result["event_type"] == "Replay Attack"
        assert result["threat_level"] == "Malicious"
