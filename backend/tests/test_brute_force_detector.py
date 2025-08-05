"""
test_brute_force_detector.py

Comprehensive tests for the enhanced BruteForceDetector implementation.
Tests temporal analysis, pattern recognition, escalating threat levels, and evidence collection.

This test suite verifies:
- Temporal analysis for detecting rapid signal attempts
- Pattern recognition for brute force attack signatures
- Escalating threat levels for repeated attempts
- Evidence collection for brute force proof
- Multi-tier rate thresholds and time windows
- Statistical analysis and consistency scoring
"""

import pytest
import time
import numpy as np
from unittest.mock import Mock

# Import the classes we're testing
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from rtl_sdr.brute_force_detector import BruteForceDetector
from rtl_sdr.signal_history_buffer import SignalHistoryBuffer
from rtl_sdr.automotive_signal_analyzer import DetectedSignal, SignalFeatures


class TestBruteForceDetector:
    """Test suite for enhanced BruteForceDetector."""

    @pytest.fixture
    def signal_history(self):
        """Create a signal history buffer for testing."""
        return SignalHistoryBuffer(max_size=1000, time_window=300)

    @pytest.fixture
    def brute_force_detector(self, signal_history):
        """Create a BruteForceDetector instance for testing."""
        return BruteForceDetector(signal_history)

    @pytest.fixture
    def sample_signal_features(self):
        """Create sample signal features for testing."""
        return SignalFeatures(
            timestamp=time.time(),
            frequency=433.92e6,
            power_spectrum=np.random.random(1024).tolist(),
            burst_timing=[0.01, 0.02, 0.03],
            modulation_type="FSK",
            frequency_deviation=25000.0,
            signal_bandwidth=50000.0,
            snr=15.0,
            rssi=-45.0,
            peak_frequencies=[433.92e6, 433.94e6],
            burst_count=3,
            inter_burst_intervals=[0.01, 0.01],
        )

    @pytest.fixture
    def sample_detected_signal(self, sample_signal_features):
        """Create a sample detected signal for testing."""
        return DetectedSignal(
            signal_type="key_fob",
            confidence=0.85,
            features=sample_signal_features,
            timestamp=time.time(),
            classification_details={
                "pattern_match": "FSK_burst",
                "frequency_band": "433MHz",
            },
        )

    def test_initialization(self, brute_force_detector):
        """Test BruteForceDetector initialization."""
        assert brute_force_detector.rate_thresholds["suspicious"] == 5
        assert brute_force_detector.rate_thresholds["moderate"] == 10
        assert brute_force_detector.rate_thresholds["high"] == 20
        assert brute_force_detector.rate_thresholds["critical"] == 40

        assert brute_force_detector.time_windows["short"] == 30
        assert brute_force_detector.time_windows["medium"] == 60
        assert brute_force_detector.time_windows["long"] == 300

        assert brute_force_detector.rapid_burst_threshold == 2.0
        assert brute_force_detector.sustained_attack_duration == 120

    def test_benign_single_signal(self, brute_force_detector, sample_detected_signal):
        """Test that a single signal is not detected as brute force."""
        result = brute_force_detector.check_brute_force(sample_detected_signal)

        assert result["is_brute_force"] == False

    def test_suspicious_rate_detection(
        self, brute_force_detector, sample_detected_signal, signal_history
    ):
        """Test detection of suspicious signal rates."""
        # Add signals at suspicious rate (6 signals per minute)
        base_time = time.time()
        for i in range(6):
            signal_data = {
                "signal_type": "key_fob",
                "features": sample_detected_signal.features.to_dict(),
                "timestamp": base_time - (60 - i * 10),  # 6 signals over 60 seconds
            }
            signal_history.add_signal(signal_data)

        result = brute_force_detector.check_brute_force(sample_detected_signal)

        assert result["is_brute_force"] == True
        assert result["confidence"] > 0.0
        assert (
            result["evidence"]["attack_classification"]["threat_level"] == "suspicious"
        )

    def test_moderate_threat_escalation(
        self, brute_force_detector, sample_detected_signal, signal_history
    ):
        """Test escalation to moderate threat level."""
        # Add signals at moderate rate (12 signals per minute)
        base_time = time.time()
        for i in range(12):
            signal_data = {
                "signal_type": "key_fob",
                "features": sample_detected_signal.features.to_dict(),
                "timestamp": base_time - (60 - i * 5),  # 12 signals over 60 seconds
            }
            signal_history.add_signal(signal_data)

        result = brute_force_detector.check_brute_force(sample_detected_signal)

        assert result["is_brute_force"] == True
        assert result["evidence"]["attack_classification"]["threat_level"] == "moderate"
        assert result["confidence"] > 0.6

    def test_high_threat_escalation(
        self, brute_force_detector, sample_detected_signal, signal_history
    ):
        """Test escalation to high threat level."""
        # Add signals at high rate (25 signals per minute)
        base_time = time.time()
        for i in range(25):
            signal_data = {
                "signal_type": "key_fob",
                "features": sample_detected_signal.features.to_dict(),
                "timestamp": base_time - (60 - i * 2.4),  # 25 signals over 60 seconds
            }
            signal_history.add_signal(signal_data)

        result = brute_force_detector.check_brute_force(sample_detected_signal)

        assert result["is_brute_force"] == True
        assert result["evidence"]["attack_classification"]["threat_level"] == "high"
        assert result["confidence"] > 0.7

    def test_critical_threat_escalation(
        self, brute_force_detector, sample_detected_signal, signal_history
    ):
        """Test escalation to critical threat level."""
        # Add signals at critical rate (45 signals per minute)
        base_time = time.time()
        for i in range(45):
            signal_data = {
                "signal_type": "key_fob",
                "features": sample_detected_signal.features.to_dict(),
                "timestamp": base_time - (60 - i * 1.33),  # 45 signals over 60 seconds
            }
            signal_history.add_signal(signal_data)

        result = brute_force_detector.check_brute_force(sample_detected_signal)

        assert result["is_brute_force"] == True
        assert result["evidence"]["attack_classification"]["threat_level"] == "critical"
        assert result["confidence"] > 0.8

    def test_rapid_burst_detection(
        self, brute_force_detector, sample_detected_signal, signal_history
    ):
        """Test detection of rapid burst patterns."""
        # Add signals with rapid bursts (< 2 seconds apart)
        base_time = time.time()
        burst_intervals = [0.5, 1.0, 1.5, 0.8, 1.2]  # All under 2 second threshold

        for i, interval in enumerate(burst_intervals):
            signal_data = {
                "signal_type": "key_fob",
                "features": sample_detected_signal.features.to_dict(),
                "timestamp": base_time - sum(burst_intervals[: i + 1]),
            }
            signal_history.add_signal(signal_data)

        result = brute_force_detector.check_brute_force(sample_detected_signal)

        assert result["is_brute_force"] == True
        assert result["evidence"]["pattern_evidence"]["burst_pattern"]["count"] > 0
        assert (
            result["evidence"]["attack_classification"]["attack_type"] == "rapid_burst"
        )

    def test_sustained_attack_detection(
        self, brute_force_detector, sample_detected_signal, signal_history
    ):
        """Test detection of sustained attacks over long periods."""
        # Add signals over 5 minute period (long-term window)
        base_time = time.time()
        for i in range(20):  # 20 signals over 5 minutes
            signal_data = {
                "signal_type": "key_fob",
                "features": sample_detected_signal.features.to_dict(),
                "timestamp": base_time
                - (300 - i * 15),  # Every 15 seconds over 5 minutes
            }
            signal_history.add_signal(signal_data)

        result = brute_force_detector.check_brute_force(sample_detected_signal)

        assert result["is_brute_force"] == True
        assert result["evidence"]["pattern_evidence"]["persistent_attack"] == True

    def test_signal_consistency_analysis(
        self, brute_force_detector, sample_detected_signal, signal_history
    ):
        """Test analysis of signal consistency (identical repeated attempts)."""
        # Add identical signals (high consistency)
        base_time = time.time()
        for i in range(5):
            signal_data = {
                "signal_type": "key_fob",
                "features": sample_detected_signal.features.to_dict(),
                "timestamp": base_time - (60 - i * 12),  # Every 12 seconds
            }
            signal_history.add_signal(signal_data)

        result = brute_force_detector.check_brute_force(sample_detected_signal)

        if result["is_brute_force"]:
            consistency = result["evidence"]["pattern_evidence"]["signal_consistency"]
            assert consistency["consistency_score"] > 0.8
            assert consistency["identical_signals"] > 0

    def test_temporal_analysis_multiple_windows(
        self, brute_force_detector, sample_detected_signal, signal_history
    ):
        """Test temporal analysis across multiple time windows."""
        # Add signals across different time windows
        base_time = time.time()

        # Short window: 3 signals in 30 seconds
        for i in range(3):
            signal_data = {
                "signal_type": "key_fob",
                "features": sample_detected_signal.features.to_dict(),
                "timestamp": base_time - (30 - i * 10),
            }
            signal_history.add_signal(signal_data)

        # Medium window: 8 signals in 60 seconds
        for i in range(5):
            signal_data = {
                "signal_type": "key_fob",
                "features": sample_detected_signal.features.to_dict(),
                "timestamp": base_time - (60 - i * 12),
            }
            signal_history.add_signal(signal_data)

        result = brute_force_detector.check_brute_force(sample_detected_signal)

        if result["is_brute_force"]:
            temporal_evidence = result["evidence"]["temporal_evidence"]
            assert "short" in temporal_evidence
            assert "medium" in temporal_evidence
            assert "long" in temporal_evidence

            assert temporal_evidence["short"]["signal_count"] >= 3
            assert temporal_evidence["medium"]["signal_count"] >= 8

    def test_evidence_collection_completeness(
        self, brute_force_detector, sample_detected_signal, signal_history
    ):
        """Test comprehensive evidence collection."""
        # Create a brute force scenario
        base_time = time.time()
        for i in range(15):  # 15 signals per minute (moderate threat)
            signal_data = {
                "signal_type": "key_fob",
                "features": sample_detected_signal.features.to_dict(),
                "timestamp": base_time - (60 - i * 4),
            }
            signal_history.add_signal(signal_data)

        result = brute_force_detector.check_brute_force(sample_detected_signal)

        assert result["is_brute_force"] == True

        evidence = result["evidence"]

        # Check attack classification
        assert "attack_classification" in evidence
        assert "threat_level" in evidence["attack_classification"]
        assert "confidence" in evidence["attack_classification"]
        assert "attack_type" in evidence["attack_classification"]

        # Check temporal evidence
        assert "temporal_evidence" in evidence
        for window in ["short", "medium", "long"]:
            assert window in evidence["temporal_evidence"]
            assert "signal_count" in evidence["temporal_evidence"][window]
            assert "signal_rate_per_minute" in evidence["temporal_evidence"][window]

        # Check pattern evidence
        assert "pattern_evidence" in evidence

        # Check signal evidence
        assert "signal_evidence" in evidence
        assert evidence["signal_evidence"]["signal_type"] == "key_fob"
        assert evidence["signal_evidence"]["frequency"] == 433.92e6

        # Check statistical analysis
        assert "statistical_analysis" in evidence
        assert "total_attempts" in evidence["statistical_analysis"]
        assert "average_interval_seconds" in evidence["statistical_analysis"]

        # Check recommended actions
        assert "recommended_actions" in evidence
        assert isinstance(evidence["recommended_actions"], list)
        assert len(evidence["recommended_actions"]) > 0

    def test_recommended_actions_by_threat_level(self, brute_force_detector):
        """Test that appropriate actions are recommended for each threat level."""
        # Test suspicious level actions
        suspicious_actions = brute_force_detector._generate_recommended_actions(
            "suspicious"
        )
        assert "Monitor signal source" in " ".join(suspicious_actions)

        # Test moderate level actions
        moderate_actions = brute_force_detector._generate_recommended_actions(
            "moderate"
        )
        assert "rate limiting" in " ".join(moderate_actions).lower()

        # Test high level actions
        high_actions = brute_force_detector._generate_recommended_actions("high")
        assert "block" in " ".join(high_actions).lower()

        # Test critical level actions
        critical_actions = brute_force_detector._generate_recommended_actions(
            "critical"
        )
        assert "EMERGENCY" in " ".join(critical_actions)

    def test_interval_consistency_calculation(self, brute_force_detector):
        """Test interval consistency scoring."""
        # Test consistent intervals
        consistent_intervals = {
            "count": 5,
            "intervals": [1.0, 1.0, 1.0, 1.0, 1.0],
            "average": 1.0,
            "std_dev": 0.0,
        }
        consistency = brute_force_detector._calculate_interval_consistency(
            consistent_intervals
        )
        assert consistency == 1.0  # Perfect consistency

        # Test inconsistent intervals
        inconsistent_intervals = {
            "count": 5,
            "intervals": [0.5, 2.0, 0.8, 3.0, 1.2],
            "average": 1.5,
            "std_dev": 1.0,
        }
        consistency = brute_force_detector._calculate_interval_consistency(
            inconsistent_intervals
        )
        assert 0.0 <= consistency < 1.0  # Lower consistency

    def test_signal_similarity_calculation(
        self, brute_force_detector, sample_detected_signal
    ):
        """Test signal similarity calculation for consistency analysis."""
        # Create a very similar signal
        similar_signal = Mock()
        similar_signal.features = Mock()
        similar_signal.features.frequency = sample_detected_signal.features.frequency
        similar_signal.features.rssi = sample_detected_signal.features.rssi
        similar_signal.features.burst_timing = (
            sample_detected_signal.features.burst_timing
        )

        similarity = brute_force_detector._calculate_signal_similarity(
            sample_detected_signal, similar_signal
        )
        assert similarity > 0.8  # High similarity

        # Create a different signal
        different_signal = Mock()
        different_signal.features = Mock()
        different_signal.features.frequency = (
            sample_detected_signal.features.frequency * 1.1
        )
        different_signal.features.rssi = sample_detected_signal.features.rssi + 20
        different_signal.features.burst_timing = [0.05, 0.06, 0.07]  # Different timing

        similarity = brute_force_detector._calculate_signal_similarity(
            sample_detected_signal, different_signal
        )
        assert similarity < 0.5  # Low similarity

    def test_performance_with_large_history(
        self, brute_force_detector, sample_detected_signal, signal_history
    ):
        """Test performance with large signal history."""
        # Add many signals to history
        base_time = time.time()
        for i in range(500):  # Large number of signals
            signal_data = {
                "signal_type": "key_fob",
                "features": sample_detected_signal.features.to_dict(),
                "timestamp": base_time - (300 - i * 0.6),  # Over 5 minutes
            }
            signal_history.add_signal(signal_data)

        # Measure processing time
        start_time = time.time()
        result = brute_force_detector.check_brute_force(sample_detected_signal)
        processing_time = time.time() - start_time

        # Should complete within reasonable time (< 1 second)
        assert processing_time < 1.0
        assert result["is_brute_force"] == True  # Should detect with this many signals

    def test_different_signal_types_isolation(
        self, brute_force_detector, signal_history
    ):
        """Test that different signal types are analyzed separately."""
        # Add many key_fob signals
        base_time = time.time()
        for i in range(15):
            signal_data = {
                "signal_type": "key_fob",
                "features": {"frequency": 433.92e6},
                "timestamp": base_time - (60 - i * 4),
            }
            signal_history.add_signal(signal_data)

        # Test with TPMS signal (different type)
        tpms_features = SignalFeatures(
            timestamp=time.time(),
            frequency=315e6,
            power_spectrum=np.random.random(1024).tolist(),
            burst_timing=[0.005, 0.010],
            modulation_type="FSK",
            frequency_deviation=15000.0,
            signal_bandwidth=30000.0,
            snr=12.0,
            rssi=-50.0,
            peak_frequencies=[315e6, 315.01e6],
            burst_count=2,
            inter_burst_intervals=[0.005],
        )

        tpms_signal = DetectedSignal(
            signal_type="tpms",
            confidence=0.80,
            features=tpms_features,
            timestamp=time.time(),
            classification_details={
                "pattern_match": "FSK_burst",
                "frequency_band": "315MHz",
            },
        )

        result = brute_force_detector.check_brute_force(tpms_signal)

        # Should not detect brute force for TPMS since key_fob signals are separate
        assert result["is_brute_force"] == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
