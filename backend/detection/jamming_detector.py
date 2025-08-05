"""
jamming_detector.py

Advanced jamming detection for RF interference patterns and denial-of-service attacks.
"""

import time
import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass
from .threat_levels import ThreatLevel


@dataclass
class JammingEvidence:
    """Evidence collected for jamming attack detection."""

    noise_floor_elevation: float
    broadband_interference: bool
    jamming_pattern_type: str
    affected_frequencies: List[float]
    interference_duration: float
    signal_to_noise_degradation: float
    jamming_confidence: float


class JammingDetector:
    """
    Advanced jamming detector for RF interference patterns and denial-of-service attacks.

    Detects jamming attacks by:
    1. Analyzing noise floor elevation across frequency bands
    2. Detecting broadband interference patterns
    3. Identifying specific jamming pattern types (continuous, pulse, sweep)
    4. Building confidence scores for jamming detection
    """

    def __init__(
        self, noise_threshold: float = 10.0, interference_threshold: float = 0.8
    ):
        """
        Initialize jamming detector.

        Args:
            noise_threshold: Minimum noise floor elevation (dB) to consider jamming
            interference_threshold: Minimum interference ratio to classify as jamming
        """
        self.noise_threshold = noise_threshold
        self.interference_threshold = interference_threshold
        self.baseline_noise_floor = {}  # Frequency -> baseline noise level
        self.jamming_patterns = {
            "continuous": self._detect_continuous_jamming,
            "pulse": self._detect_pulse_jamming,
            "sweep": self._detect_sweep_jamming,
            "spot": self._detect_spot_jamming,
        }

    def check_jamming(
        self, signal: Dict[str, Any], signal_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check if current signal conditions indicate jamming attack.

        Args:
            signal: Current signal to analyze
            signal_history: List of recent signals for baseline comparison

        Returns:
            Dictionary containing jamming detection results and evidence
        """
        # Analyze noise floor elevation
        noise_analysis = self._analyze_noise_floor(signal, signal_history)

        # Detect broadband interference
        broadband_interference = self._detect_broadband_interference(signal)

        # Identify jamming pattern type
        jamming_pattern = self._identify_jamming_pattern(signal, signal_history)

        # Calculate overall jamming confidence
        jamming_confidence = self._calculate_jamming_confidence(
            noise_analysis, broadband_interference, jamming_pattern
        )

        # Determine if this constitutes jamming
        is_jamming = jamming_confidence > self.interference_threshold

        if is_jamming:
            evidence = self._collect_jamming_evidence(
                signal,
                noise_analysis,
                broadband_interference,
                jamming_pattern,
                jamming_confidence,
            )

            # Determine threat level based on jamming severity
            if jamming_confidence > 0.9:
                threat_level = ThreatLevel.MALICIOUS
            elif jamming_confidence > 0.7:
                threat_level = ThreatLevel.SUSPICIOUS
            else:
                threat_level = ThreatLevel.BENIGN

            return {
                "is_jamming": True,
                "confidence": jamming_confidence,
                "evidence": evidence,
                "threat_level": threat_level,
                "description": f"Jamming attack detected: {jamming_pattern['type']} pattern with {jamming_confidence:.2%} confidence",
            }

        return {
            "is_jamming": False,
            "confidence": jamming_confidence,
            "evidence": None,
            "threat_level": ThreatLevel.BENIGN,
            "description": "No jamming detected",
        }

    def _analyze_noise_floor(
        self, signal: Dict[str, Any], signal_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze noise floor elevation compared to baseline.

        Args:
            signal: Current signal
            signal_history: Historical signals for baseline

        Returns:
            Dictionary with noise floor analysis results
        """
        frequency = signal.get("frequency", 0)
        current_noise = signal.get("features", {}).get("noise_floor", 0)

        # If no features or no noise floor data, return no elevation
        if not signal.get("features") or current_noise == 0:
            return {
                "current_noise": current_noise,
                "baseline_noise": 0,
                "noise_elevation": 0,
                "elevation_significant": False,
            }

        # Calculate baseline noise floor from history
        baseline_noise = self._calculate_baseline_noise(frequency, signal_history)

        # Calculate noise floor elevation
        noise_elevation = current_noise - baseline_noise if baseline_noise != 0 else 0

        return {
            "current_noise": current_noise,
            "baseline_noise": baseline_noise,
            "noise_elevation": noise_elevation,
            "elevation_significant": abs(noise_elevation) > self.noise_threshold,
        }

    def _calculate_baseline_noise(
        self, frequency: float, signal_history: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate baseline noise floor from historical signals.

        Args:
            frequency: Target frequency
            signal_history: Historical signal data

        Returns:
            Baseline noise floor level
        """
        # Get recent signals at similar frequency (within 1 MHz)
        freq_tolerance = 1e6  # 1 MHz
        relevant_signals = [
            s
            for s in signal_history[-50:]  # Last 50 signals
            if abs(s.get("frequency", 0) - frequency) < freq_tolerance
        ]

        if not relevant_signals:
            return 0.0

        # Calculate median noise floor (robust against outliers)
        noise_levels = [
            s.get("features", {}).get("noise_floor", 0)
            for s in relevant_signals
            if s.get("features", {}).get("noise_floor", 0) != 0  # Exclude zero values
        ]

        if noise_levels:
            return float(np.median(noise_levels))
        return 0.0

    def _detect_broadband_interference(self, signal: Dict[str, Any]) -> bool:
        """
        Detect broadband interference patterns.

        Args:
            signal: Signal to analyze

        Returns:
            True if broadband interference detected
        """
        features = signal.get("features", {})
        power_spectrum = features.get("power_spectrum", [])

        if not power_spectrum or len(power_spectrum) < 10:
            return False

        # Convert to numpy array for analysis
        spectrum = np.array(power_spectrum)

        # Calculate spectral flatness (measure of broadband nature)
        # High spectral flatness indicates broadband interference
        # Ensure all values are positive before taking log
        spectrum_positive = np.maximum(spectrum, 1e-10)
        geometric_mean = np.exp(np.mean(np.log(spectrum_positive)))
        arithmetic_mean = np.mean(spectrum)

        if arithmetic_mean > 0:
            spectral_flatness = geometric_mean / arithmetic_mean
            # Broadband interference typically has high spectral flatness (> 0.8) and high power
            return bool(spectral_flatness > 0.8 and arithmetic_mean > 1.0)

        return False

    def _identify_jamming_pattern(
        self, signal: Dict[str, Any], signal_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Identify the type of jamming pattern.

        Args:
            signal: Current signal
            signal_history: Historical signals

        Returns:
            Dictionary with jamming pattern analysis
        """
        # Test each jamming pattern type
        pattern_results = {}

        for pattern_name, detector_func in self.jamming_patterns.items():
            pattern_results[pattern_name] = detector_func(signal, signal_history)

        # Find the pattern with highest confidence
        best_pattern = max(pattern_results.items(), key=lambda x: x[1]["confidence"])

        return {
            "type": best_pattern[0],
            "confidence": best_pattern[1]["confidence"],
            "details": best_pattern[1],
            "all_patterns": pattern_results,
        }

    def _detect_continuous_jamming(
        self, signal: Dict[str, Any], signal_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect continuous jamming patterns.

        Args:
            signal: Current signal
            signal_history: Historical signals

        Returns:
            Continuous jamming detection results
        """
        # Look for sustained high power levels across time
        recent_signals = signal_history[-10:]  # Last 10 signals

        if len(recent_signals) < 5:
            return {"confidence": 0.0, "duration": 0.0}

        # Check for sustained power elevation
        power_levels = [s.get("features", {}).get("rssi", 0) for s in recent_signals]
        current_power = signal.get("features", {}).get("rssi", 0)
        power_levels.append(current_power)

        # Calculate power stability (low variance indicates continuous jamming)
        power_variance = np.var(power_levels) if len(power_levels) > 1 else float("inf")
        mean_power = np.mean(power_levels)

        # High power with low variance suggests continuous jamming
        if (
            mean_power > -30 and power_variance < 25
        ):  # -30 dBm threshold, 25 dB² variance threshold
            confidence = min(
                1.0, (mean_power + 50) / 50
            )  # Scale confidence based on power
            duration = len(recent_signals) * 0.1  # Assume 100ms per signal
            return {"confidence": confidence, "duration": duration}

        return {"confidence": 0.0, "duration": 0.0}

    def _detect_pulse_jamming(
        self, signal: Dict[str, Any], signal_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect pulse jamming patterns.

        Args:
            signal: Current signal
            signal_history: Historical signals

        Returns:
            Pulse jamming detection results
        """
        # Look for periodic high-power pulses
        recent_signals = signal_history[-20:]  # Last 20 signals for pattern detection

        if len(recent_signals) < 10:
            return {"confidence": 0.0, "pulse_rate": 0.0}

        # Extract power levels and timestamps
        power_data = []
        for s in recent_signals:
            power_data.append(
                {
                    "power": s.get("features", {}).get("rssi", 0),
                    "timestamp": s.get("timestamp", 0),
                }
            )

        # Add current signal
        power_data.append(
            {
                "power": signal.get("features", {}).get("rssi", 0),
                "timestamp": signal.get("timestamp", time.time()),
            }
        )

        # Detect periodic patterns in power levels
        powers = [d["power"] for d in power_data]

        # Find peaks (potential jamming pulses)
        if len(powers) > 1:
            power_threshold = np.mean(powers) + 1.5 * np.std(
                powers
            )  # 1.5 sigma above mean
        else:
            power_threshold = powers[0] if powers else 0
        peaks = [i for i, p in enumerate(powers) if p > power_threshold]

        if len(peaks) >= 3:
            # Calculate pulse intervals
            peak_intervals = np.diff([power_data[i]["timestamp"] for i in peaks])

            # Check for regularity in pulse timing
            if len(peak_intervals) > 1:
                interval_variance = np.var(peak_intervals)
                mean_interval = np.mean(peak_intervals)

                # Regular pulses have low variance in timing
                if (
                    mean_interval > 0 and interval_variance / (mean_interval**2) < 0.1
                ):  # Coefficient of variation < 0.1
                    pulse_rate = 1.0 / mean_interval if mean_interval > 0 else 0
                    confidence = min(
                        1.0, len(peaks) / 10.0
                    )  # Scale by number of detected pulses
                    return {"confidence": confidence, "pulse_rate": pulse_rate}

        return {"confidence": 0.0, "pulse_rate": 0.0}

    def _detect_sweep_jamming(
        self, signal: Dict[str, Any], signal_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect sweep jamming patterns.

        Args:
            signal: Current signal
            signal_history: Historical signals

        Returns:
            Sweep jamming detection results
        """
        # Look for systematic frequency changes with high power
        recent_signals = signal_history[-15:]  # Last 15 signals

        if len(recent_signals) < 8:
            return {"confidence": 0.0, "sweep_rate": 0.0}

        # Extract frequency and power data
        freq_power_data = []
        for s in recent_signals:
            freq_power_data.append(
                {
                    "frequency": s.get("frequency", 0),
                    "power": s.get("features", {}).get("rssi", 0),
                    "timestamp": s.get("timestamp", 0),
                }
            )

        # Add current signal
        freq_power_data.append(
            {
                "frequency": signal.get("frequency", 0),
                "power": signal.get("features", {}).get("rssi", 0),
                "timestamp": signal.get("timestamp", time.time()),
            }
        )

        # Check for systematic frequency progression
        frequencies = [d["frequency"] for d in freq_power_data]
        powers = [d["power"] for d in freq_power_data]

        # Calculate frequency changes
        freq_changes = np.diff(frequencies)

        # Look for consistent frequency progression (sweep)
        if len(freq_changes) > 3:
            # Check if frequency changes are consistent in direction
            positive_changes = sum(
                1 for fc in freq_changes if fc > 1000
            )  # > 1 kHz change
            negative_changes = sum(
                1 for fc in freq_changes if fc < -1000
            )  # < -1 kHz change

            # Sweep jamming shows consistent frequency progression
            total_changes = len(freq_changes)
            directional_consistency = (
                max(positive_changes, negative_changes) / total_changes
            )

            # High power during frequency changes indicates sweep jamming
            mean_power = np.mean(powers)

            if (
                directional_consistency > 0.6 and mean_power > -40
            ):  # 60% consistency, -40 dBm threshold
                sweep_rate = abs(np.mean(freq_changes)) / 1e6  # MHz per signal
                confidence = min(1.0, directional_consistency * (mean_power + 60) / 60)
                return {"confidence": confidence, "sweep_rate": sweep_rate}

        return {"confidence": 0.0, "sweep_rate": 0.0}

    def _detect_spot_jamming(
        self, signal: Dict[str, Any], signal_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect spot jamming patterns (narrow-band interference).

        Args:
            signal: Current signal
            signal_history: Historical signals

        Returns:
            Spot jamming detection results
        """
        # Look for high power in narrow frequency band
        features = signal.get("features", {})
        power_spectrum = features.get("power_spectrum", [])

        if not power_spectrum:
            return {"confidence": 0.0, "peak_frequency": 0.0}

        spectrum = np.array(power_spectrum)

        # Find spectral peaks
        if len(spectrum) > 10:
            # Calculate spectral peak characteristics
            max_power = np.max(spectrum)
            mean_power = np.mean(spectrum)
            peak_index = np.argmax(spectrum)

            # Calculate peak-to-average ratio
            peak_to_average = max_power / mean_power if mean_power > 0 else 0

            # Spot jamming has high peak-to-average ratio (narrow-band high power)
            # Also require high absolute power level to avoid false positives
            if (
                peak_to_average > 10.0 and max_power > 2.0
            ):  # 10:1 ratio threshold and minimum power
                # Calculate frequency of peak (simplified)
                frequency = signal.get("frequency", 0)
                sample_rate = signal.get("sample_rate", 2048000)
                freq_resolution = sample_rate / len(spectrum)
                peak_frequency = (
                    frequency + (peak_index - len(spectrum) // 2) * freq_resolution
                )

                confidence = min(1.0, peak_to_average / 10.0)  # Scale confidence
                return {"confidence": confidence, "peak_frequency": peak_frequency}

        return {"confidence": 0.0, "peak_frequency": 0.0}

    def _calculate_jamming_confidence(
        self,
        noise_analysis: Dict[str, Any],
        broadband_interference: bool,
        jamming_pattern: Dict[str, Any],
    ) -> float:
        """
        Calculate overall jamming confidence score.

        Args:
            noise_analysis: Noise floor analysis results
            broadband_interference: Broadband interference detection
            jamming_pattern: Jamming pattern analysis

        Returns:
            Overall jamming confidence (0.0 to 1.0)
        """
        confidence_factors = []

        # Noise floor elevation factor (30% weight)
        if noise_analysis["elevation_significant"]:
            noise_factor = min(
                1.0, abs(noise_analysis["noise_elevation"]) / (2 * self.noise_threshold)
            )
            confidence_factors.append(("noise", noise_factor, 0.3))

        # Broadband interference factor (20% weight)
        if broadband_interference:
            confidence_factors.append(("broadband", 1.0, 0.2))

        # Pattern detection factor (50% weight)
        pattern_confidence = jamming_pattern["confidence"]
        if pattern_confidence > 0.1:  # Only consider if pattern has some confidence
            confidence_factors.append(("pattern", pattern_confidence, 0.5))

        # Calculate weighted average
        if confidence_factors:
            weighted_sum = sum(
                confidence * weight for _, confidence, weight in confidence_factors
            )
            total_weight = sum(weight for _, _, weight in confidence_factors)
            final_confidence = weighted_sum / total_weight if total_weight > 0 else 0.0

            # Apply minimum threshold to avoid false positives from noise
            # Require at least 2 indicators or very high single indicator confidence
            if len(confidence_factors) >= 2 or (
                len(confidence_factors) == 1 and final_confidence > 0.8
            ):
                return final_confidence if final_confidence > 0.2 else 0.0
            else:
                return 0.0

        return 0.0

    def _collect_jamming_evidence(
        self,
        signal: Dict[str, Any],
        noise_analysis: Dict[str, Any],
        broadband_interference: bool,
        jamming_pattern: Dict[str, Any],
        jamming_confidence: float,
    ) -> JammingEvidence:
        """
        Collect technical evidence for jamming attack.

        Args:
            signal: Current signal
            noise_analysis: Noise analysis results
            broadband_interference: Broadband interference detection
            jamming_pattern: Pattern analysis results
            jamming_confidence: Overall confidence score

        Returns:
            JammingEvidence object with technical proof
        """
        # Determine affected frequencies
        frequency = signal.get("frequency", 0)
        sample_rate = signal.get("sample_rate", 2048000)
        bandwidth = sample_rate / 2  # Nyquist frequency

        affected_frequencies = [frequency - bandwidth / 2, frequency + bandwidth / 2]

        # Calculate interference duration (simplified)
        interference_duration = 1.0  # Assume 1 second for current implementation

        # Calculate signal-to-noise degradation
        current_snr = signal.get("features", {}).get("snr", 0)
        baseline_snr = 20.0  # Assume 20 dB baseline SNR
        snr_degradation = max(0, baseline_snr - current_snr)

        return JammingEvidence(
            noise_floor_elevation=noise_analysis["noise_elevation"],
            broadband_interference=broadband_interference,
            jamming_pattern_type=jamming_pattern["type"],
            affected_frequencies=affected_frequencies,
            interference_duration=interference_duration,
            signal_to_noise_degradation=snr_degradation,
            jamming_confidence=jamming_confidence,
        )
