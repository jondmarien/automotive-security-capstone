"""
test_jamming_detector.py

Comprehensive tests for the JammingDetector class.
"""

import pytest
import numpy as np
import time
from unittest.mock import patch

# Add the backend directory to the path for imports
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from detection.jamming_detector import JammingDetector, JammingEvidence
from detection.threat_levels import ThreatLevel


class TestJammingDetector:
    """Test suite for JammingDetector functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = JammingDetector(
            noise_threshold=10.0, interference_threshold=0.8
        )
        # Create a more realistic base signal that won't trigger false positives
        spectrum = np.random.normal(0.5, 0.1, 1024)  # Baseline noise
        spectrum[500:520] = np.random.normal(0.8, 0.05, 20)  # Small signal peak

        self.base_signal = {
            "frequency": 433.92e6,
            "timestamp": time.time(),
            "sample_rate": 2048000,
            "features": {
                "power_spectrum": spectrum.tolist(),
                "noise_floor": -80.0,
                "rssi": -50.0,
                "snr": 20.0,
                "burst_timing": [0.0, 0.01, 0.02],
            },
        }

    def test_initialization(self):
        """Test JammingDetector initialization."""
        detector = JammingDetector(noise_threshold=15.0, interference_threshold=0.9)
        assert detector.noise_threshold == 15.0
        assert detector.interference_threshold == 0.9
        assert isinstance(detector.baseline_noise_floor, dict)
        assert len(detector.jamming_patterns) == 4

    def test_no_jamming_detected(self):
        """Test normal signal with no jamming."""
        import copy

        signal_history = [copy.deepcopy(self.base_signal) for _ in range(10)]

        result = self.detector.check_jamming(
            copy.deepcopy(self.base_signal), signal_history
        )

        assert result["is_jamming"] is False
        assert result["confidence"] < 0.8
        assert result["threat_level"] == ThreatLevel.BENIGN
        assert result["evidence"] is None

    def test_noise_floor_analysis(self):
        """Test noise floor elevation analysis."""
        import copy

        # Create signal history with normal noise floor
        signal_history = []
        for i in range(10):
            signal = copy.deepcopy(self.base_signal)
            signal["features"]["noise_floor"] = -80.0 + np.random.normal(0, 2)
            signal["timestamp"] = time.time() - (10 - i) * 0.1  # Different timestamps
            signal_history.append(signal)

        # Create signal with elevated noise floor
        jamming_signal = copy.deepcopy(self.base_signal)
        jamming_signal["features"]["noise_floor"] = -60.0  # 20 dB elevation
        jamming_signal["timestamp"] = time.time()  # Current time

        noise_analysis = self.detector._analyze_noise_floor(
            jamming_signal, signal_history
        )

        assert noise_analysis["elevation_significant"] is True
        assert noise_analysis["noise_elevation"] > 15.0

    def test_broadband_interference_detection(self):
        """Test broadband interference detection."""
        import copy

        # Create signal with flat, high-power spectrum (broadband interference)
        broadband_signal = copy.deepcopy(self.base_signal)
        broadband_signal["features"]["power_spectrum"] = (
            np.ones(1024) * 2.0
        ).tolist()  # High power flat spectrum

        is_broadband = self.detector._detect_broadband_interference(broadband_signal)
        assert is_broadband is True

        # Test narrow-band signal (not broadband)
        narrowband_signal = copy.deepcopy(self.base_signal)
        spectrum = np.ones(1024) * 0.1  # Low baseline
        spectrum[500:520] = 10.0  # Narrow peak
        narrowband_signal["features"]["power_spectrum"] = spectrum.tolist()

        is_broadband = self.detector._detect_broadband_interference(narrowband_signal)
        assert is_broadband is False

    def test_continuous_jamming_detection(self):
        """Test continuous jamming pattern detection."""
        # Create signal history with sustained high power
        signal_history = []
        for i in range(10):
            signal = self.base_signal.copy()
            signal["features"]["rssi"] = -25.0  # High power
            signal["timestamp"] = time.time() - (10 - i) * 0.1
            signal_history.append(signal)

        current_signal = self.base_signal.copy()
        current_signal["features"]["rssi"] = -25.0

        result = self.detector._detect_continuous_jamming(
            current_signal, signal_history
        )

        assert result["confidence"] > 0.0
        assert result["duration"] > 0.0

    def test_pulse_jamming_detection(self):
        """Test pulse jamming pattern detection."""
        import copy

        # Create signal history with periodic high-power pulses
        signal_history = []
        base_time = time.time() - 2.0

        for i in range(20):
            signal = copy.deepcopy(self.base_signal)
            signal["timestamp"] = base_time + i * 0.1

            # Create periodic pulses every 0.5 seconds
            if i % 5 == 0:
                signal["features"]["rssi"] = -20.0  # High power pulse
            else:
                signal["features"]["rssi"] = -60.0  # Low power baseline

            signal_history.append(signal)

        current_signal = copy.deepcopy(self.base_signal)
        current_signal["features"]["rssi"] = -20.0
        current_signal["timestamp"] = base_time + 20 * 0.1

        result = self.detector._detect_pulse_jamming(current_signal, signal_history)

        assert result["confidence"] > 0.0
        assert result["pulse_rate"] > 0.0

    def test_sweep_jamming_detection(self):
        """Test sweep jamming pattern detection."""
        # Create signal history with systematic frequency changes
        signal_history = []
        base_time = time.time() - 1.5
        base_freq = 433.92e6

        for i in range(15):
            signal = self.base_signal.copy()
            signal["timestamp"] = base_time + i * 0.1
            signal["frequency"] = base_freq + i * 100000  # 100 kHz steps
            signal["features"]["rssi"] = -30.0  # High power during sweep
            signal_history.append(signal)

        current_signal = self.base_signal.copy()
        current_signal["frequency"] = base_freq + 15 * 100000
        current_signal["features"]["rssi"] = -30.0
        current_signal["timestamp"] = base_time + 15 * 0.1

        result = self.detector._detect_sweep_jamming(current_signal, signal_history)

        assert result["confidence"] > 0.0
        assert result["sweep_rate"] > 0.0

    def test_spot_jamming_detection(self):
        """Test spot jamming pattern detection."""
        # Create signal with high peak-to-average ratio and sufficient power
        spot_signal = self.base_signal.copy()
        spectrum = np.ones(1024) * 0.1  # Low baseline
        spectrum[500:510] = 5.0  # High narrow peak (50:1 ratio, power > 2.0)
        spot_signal["features"]["power_spectrum"] = spectrum.tolist()

        result = self.detector._detect_spot_jamming(spot_signal, [])

        assert result["confidence"] > 0.0
        assert result["peak_frequency"] > 0.0

    def test_spot_jamming_false_positive_prevention(self):
        """Test that spot jamming detection avoids false positives with new thresholds."""
        # Test case 1: High peak-to-average ratio but low absolute power (should not detect)
        low_power_signal = self.base_signal.copy()
        spectrum = np.ones(1024) * 0.01  # Very low baseline
        spectrum[500:510] = 0.5  # Peak gives 50:1 ratio but max power < 2.0
        low_power_signal["features"]["power_spectrum"] = spectrum.tolist()

        result = self.detector._detect_spot_jamming(low_power_signal, [])
        assert (
            result["confidence"] == 0.0
        )  # Should not detect due to low absolute power

        # Test case 2: High absolute power but low peak-to-average ratio (should not detect)
        low_ratio_signal = self.base_signal.copy()
        spectrum = np.ones(1024) * 1.0  # High baseline
        spectrum[500:510] = 5.0  # Peak gives only 5:1 ratio (below 10.0 threshold)
        low_ratio_signal["features"]["power_spectrum"] = spectrum.tolist()

        result = self.detector._detect_spot_jamming(low_ratio_signal, [])
        assert (
            result["confidence"] == 0.0
        )  # Should not detect due to low peak-to-average ratio

    def test_jamming_confidence_calculation(self):
        """Test overall jamming confidence calculation."""
        noise_analysis = {"elevation_significant": True, "noise_elevation": 20.0}
        broadband_interference = True
        jamming_pattern = {"confidence": 0.8, "type": "continuous"}

        confidence = self.detector._calculate_jamming_confidence(
            noise_analysis, broadband_interference, jamming_pattern
        )

        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # Should be high with all indicators present

    def test_high_confidence_jamming_detection(self):
        """Test detection of high-confidence jamming attack."""
        import copy

        # Create signal history with normal conditions
        signal_history = []
        for i in range(10):
            signal = copy.deepcopy(self.base_signal)
            signal["features"]["noise_floor"] = -80.0
            signal["features"]["rssi"] = -50.0
            signal_history.append(signal)

        # Create jamming signal with multiple indicators
        jamming_signal = copy.deepcopy(self.base_signal)
        jamming_signal["features"]["noise_floor"] = -50.0  # 30 dB elevation
        jamming_signal["features"]["rssi"] = -20.0  # High power
        jamming_signal["features"]["power_spectrum"] = np.ones(
            1024
        ).tolist()  # Broadband

        result = self.detector.check_jamming(jamming_signal, signal_history)

        assert result["is_jamming"] is True
        assert result["confidence"] > 0.8
        assert result["threat_level"] in [ThreatLevel.SUSPICIOUS, ThreatLevel.MALICIOUS]
        assert isinstance(result["evidence"], JammingEvidence)

    def test_jamming_evidence_collection(self):
        """Test jamming evidence collection."""
        noise_analysis = {"noise_elevation": 25.0, "elevation_significant": True}
        jamming_pattern = {"type": "continuous", "confidence": 0.9}

        evidence = self.detector._collect_jamming_evidence(
            self.base_signal, noise_analysis, True, jamming_pattern, 0.85
        )

        assert isinstance(evidence, JammingEvidence)
        assert evidence.noise_floor_elevation == 25.0
        assert evidence.broadband_interference is True
        assert evidence.jamming_pattern_type == "continuous"
        assert evidence.jamming_confidence == 0.85
        assert len(evidence.affected_frequencies) == 2

    def test_baseline_noise_calculation(self):
        """Test baseline noise floor calculation."""
        # Create signal history with consistent noise floor
        signal_history = []
        target_freq = 433.92e6

        for i in range(20):
            signal = self.base_signal.copy()
            signal["frequency"] = target_freq + np.random.normal(
                0, 500000
            )  # Within 500 kHz
            signal["features"]["noise_floor"] = -80.0 + np.random.normal(0, 2)
            signal_history.append(signal)

        baseline = self.detector._calculate_baseline_noise(target_freq, signal_history)

        assert -85.0 < baseline < -75.0  # Should be around -80 dB

    def test_empty_signal_history(self):
        """Test behavior with empty signal history."""
        import copy

        result = self.detector.check_jamming(copy.deepcopy(self.base_signal), [])

        assert result["is_jamming"] is False
        assert result["confidence"] >= 0.0
        assert result["threat_level"] == ThreatLevel.BENIGN

    def test_malformed_signal_data(self):
        """Test handling of malformed signal data."""
        import copy

        # Signal with missing features
        malformed_signal = {"frequency": 433.92e6, "timestamp": time.time()}

        result = self.detector.check_jamming(
            malformed_signal, [copy.deepcopy(self.base_signal)]
        )

        assert result["is_jamming"] is False
        assert result["confidence"] >= 0.0

    def test_pattern_identification(self):
        """Test jamming pattern identification."""
        signal_history = [self.base_signal.copy() for _ in range(10)]

        pattern_result = self.detector._identify_jamming_pattern(
            self.base_signal, signal_history
        )

        assert "type" in pattern_result
        assert "confidence" in pattern_result
        assert "details" in pattern_result
        assert "all_patterns" in pattern_result
        assert pattern_result["type"] in ["continuous", "pulse", "sweep", "spot"]

    def test_threat_level_classification(self):
        """Test threat level classification based on confidence."""
        # Test high confidence (malicious)
        with patch.object(
            self.detector, "_calculate_jamming_confidence", return_value=0.95
        ):
            result = self.detector.check_jamming(self.base_signal, [])
            assert result["threat_level"] == ThreatLevel.MALICIOUS

        # Test medium confidence (suspicious)
        with patch.object(
            self.detector, "_calculate_jamming_confidence", return_value=0.85
        ):
            result = self.detector.check_jamming(self.base_signal, [])
            assert result["threat_level"] == ThreatLevel.SUSPICIOUS

        # Test low confidence (benign)
        with patch.object(
            self.detector, "_calculate_jamming_confidence", return_value=0.5
        ):
            result = self.detector.check_jamming(self.base_signal, [])
            assert result["threat_level"] == ThreatLevel.BENIGN


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
