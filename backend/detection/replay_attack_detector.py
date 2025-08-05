"""
replay_attack_detector.py

Advanced replay attack detection using signal similarity analysis and timing anomaly detection.
"""

import time
import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass
from .threat_levels import ThreatLevel


@dataclass
class ReplayEvidence:
    """Evidence collected for replay attack detection."""

    original_timestamp: float
    replay_timestamp: float
    signal_similarity: float
    timing_anomaly: Dict[str, Any]
    power_spectrum_correlation: float
    burst_timing_similarity: float
    frequency_deviation: float


class ReplayAttackDetector:
    """
    Advanced replay attack detector using signal similarity analysis.

    Detects replay attacks by:
    1. Comparing power spectrum correlation between signals
    2. Analyzing timing anomalies in signal patterns
    3. Detecting identical signals with suspicious timing characteristics
    4. Collecting technical evidence for proof of replay attacks
    """

    def __init__(self, similarity_threshold: float = 0.95, time_window: int = 300):
        """
        Initialize replay attack detector.

        Args:
            similarity_threshold: Minimum similarity score to consider signals identical
            time_window: Time window in seconds to check for replay attacks
        """
        self.similarity_threshold = similarity_threshold
        self.time_window = time_window
        self.signal_history: List[Dict[str, Any]] = []

    def check_replay(
        self, signal: Dict[str, Any], signal_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check if a signal is a replay attack by comparing with recent signals.

        Args:
            signal: Current signal to analyze
            signal_history: List of recent signals for comparison

        Returns:
            Dictionary containing replay detection results and evidence
        """
        recent_signals = self._get_recent_signals(signal_history, self.time_window)

        for historical_signal in recent_signals:
            similarity = self._calculate_signal_similarity(signal, historical_signal)

            if similarity > self.similarity_threshold:
                # Check timing characteristics for replay patterns
                if self._has_replay_timing_characteristics(signal, historical_signal):
                    evidence = self._collect_replay_evidence(
                        signal, historical_signal, similarity
                    )

                    return {
                        "is_replay": True,
                        "confidence": similarity,
                        "evidence": evidence,
                        "threat_level": ThreatLevel.MALICIOUS,
                        "description": f"Replay attack detected with {similarity:.2%} similarity",
                    }

        return {
            "is_replay": False,
            "confidence": 0.0,
            "evidence": None,
            "threat_level": ThreatLevel.BENIGN,
            "description": "No replay attack detected",
        }

    def _get_recent_signals(
        self, signal_history: List[Dict[str, Any]], time_window: int
    ) -> List[Dict[str, Any]]:
        """Get signals within the specified time window."""
        current_time = time.time()
        return [
            signal
            for signal in signal_history
            if current_time - signal.get("timestamp", 0) <= time_window
        ]

    def _calculate_signal_similarity(
        self, signal1: Dict[str, Any], signal2: Dict[str, Any]
    ) -> float:
        """
        Calculate similarity between two signals using multiple metrics.

        Args:
            signal1: First signal for comparison
            signal2: Second signal for comparison

        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Extract signal features
        features1 = signal1.get("features", {})
        features2 = signal2.get("features", {})

        # Compare power spectrum (70% weight)
        spectrum_similarity = self._compare_power_spectra(
            features1.get("power_spectrum", []), features2.get("power_spectrum", [])
        )

        # Compare burst timing (30% weight)
        timing_similarity = self._compare_burst_timing(
            features1.get("burst_timing", []), features2.get("burst_timing", [])
        )

        # Weighted average similarity
        total_similarity = 0.7 * spectrum_similarity + 0.3 * timing_similarity

        return min(1.0, max(0.0, total_similarity))

    def _compare_power_spectra(
        self, spectrum1: List[float], spectrum2: List[float]
    ) -> float:
        """
        Compare power spectra using correlation analysis.

        Args:
            spectrum1: First power spectrum
            spectrum2: Second power spectrum

        Returns:
            Correlation coefficient between spectra
        """
        if not spectrum1 or not spectrum2:
            return 0.0

        # Convert to numpy arrays for efficient computation
        spec1 = np.array(spectrum1)
        spec2 = np.array(spectrum2)

        # Ensure same length by padding or truncating
        min_len = min(len(spec1), len(spec2))
        if min_len == 0:
            return 0.0

        spec1 = spec1[:min_len]
        spec2 = spec2[:min_len]

        # Calculate normalized cross-correlation
        try:
            correlation = np.corrcoef(spec1, spec2)[0, 1]
            return abs(correlation) if not np.isnan(correlation) else 0.0
        except (ValueError, IndexError):
            return 0.0

    def _compare_burst_timing(
        self, timing1: List[float], timing2: List[float]
    ) -> float:
        """
        Compare burst timing patterns between signals.

        Args:
            timing1: First signal's burst timing
            timing2: Second signal's burst timing

        Returns:
            Timing similarity score
        """
        if not timing1 or not timing2:
            return 0.0

        # Compare number of bursts
        if len(timing1) != len(timing2):
            return 0.0

        # Calculate timing intervals
        intervals1 = np.diff(timing1) if len(timing1) > 1 else np.array([])
        intervals2 = np.diff(timing2) if len(timing2) > 1 else np.array([])

        if len(intervals1) == 0 or len(intervals2) == 0:
            return 1.0 if len(intervals1) == len(intervals2) else 0.0

        # Compare interval patterns
        try:
            # Calculate relative difference in intervals
            max_diff = np.max(np.abs(intervals1 - intervals2))
            avg_interval = np.mean(np.concatenate([intervals1, intervals2]))

            if avg_interval == 0:
                return 1.0 if max_diff == 0 else 0.0

            # Similarity decreases with relative timing difference
            relative_diff = max_diff / avg_interval
            return max(0.0, 1.0 - relative_diff)
        except (ValueError, ZeroDivisionError):
            return 0.0

    def _has_replay_timing_characteristics(
        self, signal: Dict[str, Any], historical_signal: Dict[str, Any]
    ) -> bool:
        """
        Check if timing characteristics indicate a replay attack.

        Args:
            signal: Current signal
            historical_signal: Historical signal for comparison

        Returns:
            True if timing characteristics suggest replay attack
        """
        current_time = signal.get("timestamp", time.time())
        historical_time = historical_signal.get("timestamp", 0)

        time_diff = current_time - historical_time

        # Replay attacks typically occur within a reasonable time window
        # but not immediately (which would be normal retransmission)
        min_replay_delay = 1.0  # 1 second minimum
        max_replay_delay = 300.0  # 5 minutes maximum

        if not (min_replay_delay <= time_diff <= max_replay_delay):
            return False

        # Check for timing anomalies in signal structure
        return self._detect_timing_anomalies(signal, historical_signal)

    def _detect_timing_anomalies(
        self, signal: Dict[str, Any], historical_signal: Dict[str, Any]
    ) -> bool:
        """
        Detect timing anomalies that suggest replay attacks.

        Args:
            signal: Current signal
            historical_signal: Historical signal for comparison

        Returns:
            True if timing anomalies detected
        """
        features1 = signal.get("features", {})
        features2 = historical_signal.get("features", {})

        # Check for identical burst patterns (suspicious for replay)
        timing1 = features1.get("burst_timing", [])
        timing2 = features2.get("burst_timing", [])

        if timing1 and timing2 and len(timing1) == len(timing2):
            # Calculate timing precision - replayed signals often have identical timing
            timing_diff = np.array(timing1) - np.array(timing2)
            timing_precision = (
                np.std(timing_diff)
                if len(timing_diff) > 1
                else abs(timing_diff[0])
                if len(timing_diff) == 1
                else 0
            )

            # Suspiciously precise timing (< 1ms difference) suggests replay
            if timing_precision < 0.001:
                return True

        # Check for power level anomalies
        power1 = features1.get("rssi", 0)
        power2 = features2.get("rssi", 0)

        # Significant power difference with identical signals suggests relay/replay
        power_diff = abs(power1 - power2)
        if power_diff > 10:  # > 10 dB difference
            return True

        return False

    def _collect_replay_evidence(
        self,
        signal: Dict[str, Any],
        historical_signal: Dict[str, Any],
        similarity: float,
    ) -> ReplayEvidence:
        """
        Collect technical evidence for replay attack.

        Args:
            signal: Current signal
            historical_signal: Historical signal
            similarity: Overall similarity score

        Returns:
            ReplayEvidence object with technical proof
        """
        features1 = signal.get("features", {})
        features2 = historical_signal.get("features", {})

        # Calculate detailed similarity metrics
        power_correlation = self._compare_power_spectra(
            features1.get("power_spectrum", []), features2.get("power_spectrum", [])
        )

        timing_similarity = self._compare_burst_timing(
            features1.get("burst_timing", []), features2.get("burst_timing", [])
        )

        # Analyze timing anomaly details
        timing_anomaly = self._analyze_timing_anomaly(signal, historical_signal)

        # Calculate frequency deviation
        freq1 = signal.get("frequency", 0)
        freq2 = historical_signal.get("frequency", 0)
        frequency_deviation = abs(freq1 - freq2)

        return ReplayEvidence(
            original_timestamp=historical_signal.get("timestamp", 0),
            replay_timestamp=signal.get("timestamp", time.time()),
            signal_similarity=similarity,
            timing_anomaly=timing_anomaly,
            power_spectrum_correlation=power_correlation,
            burst_timing_similarity=timing_similarity,
            frequency_deviation=frequency_deviation,
        )

    def _analyze_timing_anomaly(
        self, signal: Dict[str, Any], historical_signal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze timing anomalies between signals.

        Args:
            signal: Current signal
            historical_signal: Historical signal

        Returns:
            Dictionary with timing anomaly analysis
        """
        features1 = signal.get("features", {})
        features2 = historical_signal.get("features", {})

        timing1 = features1.get("burst_timing", [])
        timing2 = features2.get("burst_timing", [])

        anomaly_details = {
            "burst_count_match": len(timing1) == len(timing2),
            "timing_precision": 0.0,
            "power_difference": 0.0,
            "frequency_stability": True,
        }

        if timing1 and timing2 and len(timing1) == len(timing2):
            # Calculate timing precision
            timing_diff = np.array(timing1) - np.array(timing2)
            anomaly_details["timing_precision"] = (
                float(np.std(timing_diff))
                if len(timing_diff) > 1
                else float(abs(timing_diff[0]))
                if len(timing_diff) == 1
                else 0.0
            )

        # Power difference analysis
        power1 = features1.get("rssi", 0)
        power2 = features2.get("rssi", 0)
        anomaly_details["power_difference"] = abs(power1 - power2)

        # Frequency stability analysis
        freq1 = signal.get("frequency", 0)
        freq2 = historical_signal.get("frequency", 0)
        freq_diff = abs(freq1 - freq2)
        anomaly_details["frequency_stability"] = freq_diff < 1000  # Within 1 kHz

        return anomaly_details
