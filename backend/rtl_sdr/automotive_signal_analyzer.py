"""
automotive_signal_analyzer.py

Advanced automotive signal analysis for RTL-SDR signal processing.
Implements sophisticated signal feature extraction, pattern recognition, and classification
specifically designed for automotive RF signals including key fobs and TPMS.

This module provides the AutomotiveSignalAnalyzer class which performs:
- Real-time signal feature extraction from IQ samples
- Key fob pattern recognition using FSK characteristics
- TPMS signal detection and classification
- Confidence scoring for detected automotive signals
- Power spectrum analysis and burst detection

Example usage:
    analyzer = AutomotiveSignalAnalyzer()
    features = analyzer.extract_features(complex_samples)
    signals = analyzer.detect_automotive_patterns(features)
"""

import numpy as np
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from scipy import signal as scipy_signal
from scipy.fft import fft, fftfreq
import logging

logger = logging.getLogger(__name__)


@dataclass
class SignalFeatures:
    """Container for extracted signal features."""

    timestamp: float
    frequency: float
    power_spectrum: np.ndarray
    burst_timing: List[float]
    modulation_type: str
    frequency_deviation: float
    signal_bandwidth: float
    snr: float
    rssi: float
    peak_frequencies: List[float]
    burst_count: int
    inter_burst_intervals: List[float]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "frequency": self.frequency,
            "power_spectrum": self.power_spectrum.tolist()
            if isinstance(self.power_spectrum, np.ndarray)
            else self.power_spectrum,
            "burst_timing": self.burst_timing,
            "modulation_type": self.modulation_type,
            "frequency_deviation": self.frequency_deviation,
            "signal_bandwidth": self.signal_bandwidth,
            "snr": self.snr,
            "rssi": self.rssi,
            "peak_frequencies": self.peak_frequencies,
            "burst_count": self.burst_count,
            "inter_burst_intervals": self.inter_burst_intervals,
        }


@dataclass
class DetectedSignal:
    """Container for detected automotive signal."""

    signal_type: str
    confidence: float
    features: SignalFeatures
    timestamp: float
    classification_details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "signal_type": self.signal_type,
            "confidence": self.confidence,
            "features": self.features.to_dict(),
            "timestamp": self.timestamp,
            "classification_details": self.classification_details,
        }


class AutomotiveSignalAnalyzer:
    """
    Advanced automotive signal analyzer for RTL-SDR signal processing.

    This class implements sophisticated signal processing algorithms specifically
    designed for automotive RF signals including key fobs, TPMS, and other
    vehicle communication systems.
    """

    def __init__(self, sample_rate: float = 2048000):
        """
        Initialize the automotive signal analyzer.

        Args:
            sample_rate: Sample rate in Hz (default: 2.048 MS/s)
        """
        self.sample_rate = sample_rate
        self.frequency_bands = {
            "north_america_keyfob": 315e6,
            "europe_keyfob": 433.92e6,
            "japan_keyfob": 315e6,
            "tpms_315": 315e6,
            "tpms_433": 433.92e6,
        }

        # Key fob signature patterns
        self.key_fob_patterns = self._load_key_fob_signatures()

        # TPMS signature patterns
        self.tpms_patterns = self._load_tpms_signatures()

        # Detection thresholds
        self.detection_thresholds = {
            "min_snr": 10.0,  # dB
            "min_burst_count": 3,
            "max_burst_count": 8,
            "min_confidence": 0.6,
            "key_fob_bandwidth": (10e3, 100e3),  # Hz
            "tpms_bandwidth": (5e3, 50e3),  # Hz
        }

        logger.info(
            f"AutomotiveSignalAnalyzer initialized with sample_rate={sample_rate}"
        )

    def _load_key_fob_signatures(self) -> Dict[str, Dict[str, Any]]:
        """Load known key fob signature patterns."""
        return {
            "standard_keyfob": {
                "modulation": "FSK",
                "burst_count_range": (3, 5),
                "inter_burst_interval": (10e-3, 20e-3),  # 10-20ms
                "frequency_deviation": (20e3, 50e3),  # 20-50 kHz
                "burst_duration": (1e-3, 5e-3),  # 1-5ms
                "bandwidth": (20e3, 80e3),  # 20-80 kHz
                "rolling_code_pattern": True,
            },
            "bmw_keyfob": {
                "modulation": "FSK",
                "burst_count_range": (4, 6),
                "inter_burst_interval": (12e-3, 18e-3),
                "frequency_deviation": (25e3, 45e3),
                "burst_duration": (2e-3, 4e-3),
                "bandwidth": (30e3, 70e3),
                "rolling_code_pattern": True,
            },
        }

    def _load_tpms_signatures(self) -> Dict[str, Dict[str, Any]]:
        """Load known TPMS signature patterns."""
        return {
            "standard_tpms": {
                "modulation": "FSK",
                "burst_count_range": (1, 3),
                "transmission_interval": (30, 300),  # seconds
                "frequency_deviation": (10e3, 30e3),
                "burst_duration": (5e-3, 15e-3),
                "bandwidth": (10e3, 40e3),
                "data_rate": (9600, 19200),  # bps
            }
        }

    def extract_features(self, complex_samples: np.ndarray) -> SignalFeatures:
        """
        Extract comprehensive signal features from IQ samples.

        Args:
            complex_samples: Complex IQ samples from RTL-SDR

        Returns:
            SignalFeatures object containing extracted features
        """
        timestamp = time.time()

        # Power spectrum analysis
        power_spectrum = self._compute_power_spectrum(complex_samples)

        # Burst timing analysis
        burst_timing = self._detect_burst_timing(complex_samples)

        # Modulation classification
        modulation_type = self._classify_modulation(complex_samples)

        # Frequency deviation measurement
        frequency_deviation = self._measure_frequency_deviation(complex_samples)

        # Signal bandwidth measurement
        signal_bandwidth = self._measure_bandwidth(complex_samples, power_spectrum)

        # SNR and RSSI calculation
        snr = self._calculate_snr(complex_samples)
        rssi = self._calculate_rssi(complex_samples)

        # Peak frequency detection
        peak_frequencies = self._find_peak_frequencies(power_spectrum)

        # Inter-burst interval analysis
        inter_burst_intervals = self._calculate_inter_burst_intervals(burst_timing)

        return SignalFeatures(
            timestamp=timestamp,
            frequency=0.0,  # Will be set by caller based on RTL-SDR tuning
            power_spectrum=power_spectrum,
            burst_timing=burst_timing,
            modulation_type=modulation_type,
            frequency_deviation=frequency_deviation,
            signal_bandwidth=signal_bandwidth,
            snr=snr,
            rssi=rssi,
            peak_frequencies=peak_frequencies,
            burst_count=len(burst_timing),
            inter_burst_intervals=inter_burst_intervals,
        )

    def _compute_power_spectrum(self, complex_samples: np.ndarray) -> np.ndarray:
        """Compute power spectrum using FFT."""
        # Apply window function to reduce spectral leakage
        windowed_samples = complex_samples * np.hanning(len(complex_samples))

        # Compute FFT
        fft_result = fft(windowed_samples)

        # Calculate power spectrum
        power_spectrum = np.abs(fft_result) ** 2

        # Convert to dB
        power_spectrum_db = 10 * np.log10(power_spectrum + 1e-12)

        return power_spectrum_db

    def _detect_burst_timing(self, complex_samples: np.ndarray) -> List[float]:
        """Detect burst timing patterns in the signal."""
        if len(complex_samples) == 0:
            return []

        # Calculate instantaneous power
        instantaneous_power = np.abs(complex_samples) ** 2

        # Smooth the power signal
        window_size = max(1, int(self.sample_rate * 0.001))  # 1ms window, minimum 1
        if window_size >= len(instantaneous_power):
            window_size = max(1, len(instantaneous_power) // 10)

        smoothed_power = np.convolve(
            instantaneous_power, np.ones(window_size) / window_size, mode="same"
        )

        # Detect bursts using adaptive threshold
        mean_power = np.mean(smoothed_power)
        std_power = np.std(smoothed_power)

        # Use a more sensitive threshold if std is very small
        if std_power < mean_power * 0.1:
            threshold = mean_power + max(std_power, mean_power * 0.5)
        else:
            threshold = (
                mean_power + 2 * std_power
            )  # Reduced from 3 to 2 for better sensitivity

        # Find burst start times
        burst_indices = np.where(smoothed_power > threshold)[0]

        if len(burst_indices) == 0:
            return []

        # Group consecutive indices into bursts
        burst_starts = []
        current_burst_start = burst_indices[0]
        gap_threshold = max(
            window_size, int(self.sample_rate * 0.005)
        )  # 5ms gap minimum

        for i in range(1, len(burst_indices)):
            if burst_indices[i] - burst_indices[i - 1] > gap_threshold:
                # End of current burst, start of new burst
                burst_starts.append(current_burst_start / self.sample_rate)
                current_burst_start = burst_indices[i]

        # Add the last burst
        burst_starts.append(current_burst_start / self.sample_rate)

        return burst_starts

    def _classify_modulation(self, complex_samples: np.ndarray) -> str:
        """Classify the modulation type of the signal."""
        # Calculate instantaneous frequency
        instantaneous_phase = np.unwrap(np.angle(complex_samples))
        instantaneous_freq = (
            np.diff(instantaneous_phase) * self.sample_rate / (2 * np.pi)
        )

        # Analyze frequency characteristics
        freq_std = np.std(instantaneous_freq)
        freq_range = np.max(instantaneous_freq) - np.min(instantaneous_freq)

        # Simple classification based on frequency characteristics
        if freq_range > 10e3 and freq_std > 5e3:
            return "FSK"  # Frequency Shift Keying
        elif freq_std < 1e3:
            return "ASK"  # Amplitude Shift Keying
        else:
            return "Unknown"

    def _measure_frequency_deviation(self, complex_samples: np.ndarray) -> float:
        """Measure frequency deviation for FSK signals."""
        # Calculate instantaneous frequency
        instantaneous_phase = np.unwrap(np.angle(complex_samples))
        instantaneous_freq = (
            np.diff(instantaneous_phase) * self.sample_rate / (2 * np.pi)
        )

        # Remove DC component
        instantaneous_freq = instantaneous_freq - np.mean(instantaneous_freq)

        # Calculate frequency deviation as peak-to-peak frequency swing
        freq_deviation = (np.max(instantaneous_freq) - np.min(instantaneous_freq)) / 2

        return freq_deviation

    def _measure_bandwidth(
        self, complex_samples: np.ndarray, power_spectrum: np.ndarray
    ) -> float:
        """Measure signal bandwidth using power spectrum."""
        # Find the frequency bins
        freqs = fftfreq(len(complex_samples), 1 / self.sample_rate)

        # Find the peak frequency
        peak_idx = np.argmax(power_spectrum)

        # Find -3dB bandwidth
        peak_power = power_spectrum[peak_idx]
        threshold = peak_power - 3  # -3dB

        # Find frequencies where power is above threshold
        above_threshold = power_spectrum > threshold

        if not np.any(above_threshold):
            return 0.0

        # Find the bandwidth
        freq_indices = np.where(above_threshold)[0]
        min_freq_idx = np.min(freq_indices)
        max_freq_idx = np.max(freq_indices)

        bandwidth = abs(freqs[max_freq_idx] - freqs[min_freq_idx])

        return bandwidth

    def _calculate_snr(self, complex_samples: np.ndarray) -> float:
        """Calculate Signal-to-Noise Ratio."""
        # Calculate signal power (peak power)
        instantaneous_power = np.abs(complex_samples) ** 2
        signal_power = np.max(instantaneous_power)

        # Estimate noise power (median power as noise floor estimate)
        noise_power = np.median(instantaneous_power)

        # Calculate SNR in dB
        if noise_power > 0:
            snr_db = 10 * np.log10(signal_power / noise_power)
        else:
            snr_db = 0.0

        return snr_db

    def _calculate_rssi(self, complex_samples: np.ndarray) -> float:
        """Calculate Received Signal Strength Indicator."""
        # Calculate average power
        instantaneous_power = np.abs(complex_samples) ** 2
        average_power = np.mean(instantaneous_power)

        # Convert to dBm (assuming 50 ohm impedance and proper calibration)
        # This is a simplified calculation - real RSSI would need calibration
        rssi_dbm = 10 * np.log10(average_power + 1e-12) - 30  # Rough conversion

        return rssi_dbm

    def _find_peak_frequencies(self, power_spectrum: np.ndarray) -> List[float]:
        """Find peak frequencies in the power spectrum."""
        # Find peaks using scipy
        peaks, properties = scipy_signal.find_peaks(
            power_spectrum, height=np.max(power_spectrum) - 10, distance=10
        )

        # Convert peak indices to frequencies
        freqs = fftfreq(len(power_spectrum), 1 / self.sample_rate)
        peak_frequencies = [abs(freqs[peak]) for peak in peaks]

        return sorted(peak_frequencies)

    def _calculate_inter_burst_intervals(
        self, burst_timing: List[float]
    ) -> List[float]:
        """Calculate intervals between bursts."""
        if len(burst_timing) < 2:
            return []

        intervals = []
        for i in range(1, len(burst_timing)):
            interval = burst_timing[i] - burst_timing[i - 1]
            intervals.append(interval)

        return intervals

    def detect_automotive_patterns(
        self, features: SignalFeatures
    ) -> List[DetectedSignal]:
        """
        Detect patterns specific to automotive devices.

        Args:
            features: Extracted signal features

        Returns:
            List of detected automotive signals
        """
        detected_signals = []

        # Key fob detection
        key_fob_result = self._detect_key_fob_pattern(features)
        if key_fob_result:
            detected_signals.append(key_fob_result)

        # TPMS detection
        tpms_result = self._detect_tpms_pattern(features)
        if tpms_result:
            detected_signals.append(tpms_result)

        return detected_signals

    def _detect_key_fob_pattern(
        self, features: SignalFeatures
    ) -> Optional[DetectedSignal]:
        """Detect key fob specific patterns."""
        confidence = 0.0
        classification_details = {}

        # Check modulation type
        if features.modulation_type == "FSK":
            confidence += 0.3
            classification_details["modulation_match"] = True

        # Check burst count
        if (
            self.detection_thresholds["min_burst_count"]
            <= features.burst_count
            <= self.detection_thresholds["max_burst_count"]
        ):
            confidence += 0.2
            classification_details["burst_count_match"] = True

        # Check inter-burst intervals
        if features.inter_burst_intervals:
            avg_interval = np.mean(features.inter_burst_intervals)
            if 10e-3 <= avg_interval <= 20e-3:  # 10-20ms typical for key fobs
                confidence += 0.2
                classification_details["timing_match"] = True

        # Check frequency deviation
        if 20e3 <= features.frequency_deviation <= 50e3:  # Typical FSK deviation
            confidence += 0.15
            classification_details["deviation_match"] = True

        # Check signal bandwidth
        min_bw, max_bw = self.detection_thresholds["key_fob_bandwidth"]
        if min_bw <= features.signal_bandwidth <= max_bw:
            confidence += 0.1
            classification_details["bandwidth_match"] = True

        # Check SNR
        if features.snr >= self.detection_thresholds["min_snr"]:
            confidence += 0.05
            classification_details["snr_adequate"] = True

        # Only return detection if confidence is above threshold
        if confidence >= self.detection_thresholds["min_confidence"]:
            return DetectedSignal(
                signal_type="key_fob",
                confidence=confidence,
                features=features,
                timestamp=features.timestamp,
                classification_details=classification_details,
            )

        return None

    def _detect_tpms_pattern(
        self, features: SignalFeatures
    ) -> Optional[DetectedSignal]:
        """Detect TPMS (Tire Pressure Monitoring System) patterns."""
        confidence = 0.0
        classification_details = {}

        # Check modulation type
        if features.modulation_type == "FSK":
            confidence += 0.3
            classification_details["modulation_match"] = True

        # TPMS typically has fewer, longer bursts than key fobs
        if 1 <= features.burst_count <= 3:
            confidence += 0.25
            classification_details["burst_count_match"] = True

        # Check frequency deviation (typically lower than key fobs)
        if 10e3 <= features.frequency_deviation <= 30e3:
            confidence += 0.2
            classification_details["deviation_match"] = True

        # Check signal bandwidth
        min_bw, max_bw = self.detection_thresholds["tpms_bandwidth"]
        if min_bw <= features.signal_bandwidth <= max_bw:
            confidence += 0.15
            classification_details["bandwidth_match"] = True

        # Check SNR
        if features.snr >= self.detection_thresholds["min_snr"]:
            confidence += 0.1
            classification_details["snr_adequate"] = True

        # Only return detection if confidence is above threshold
        if confidence >= self.detection_thresholds["min_confidence"]:
            return DetectedSignal(
                signal_type="tpms",
                confidence=confidence,
                features=features,
                timestamp=features.timestamp,
                classification_details=classification_details,
            )

        return None

    def calculate_confidence_score(
        self, signal_type: str, features: SignalFeatures
    ) -> float:
        """
        Calculate confidence score for a detected signal.

        Args:
            signal_type: Type of detected signal
            features: Signal features

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if signal_type == "key_fob":
            return self._calculate_key_fob_confidence(features)
        elif signal_type == "tpms":
            return self._calculate_tpms_confidence(features)
        else:
            return 0.0

    def _calculate_key_fob_confidence(self, features: SignalFeatures) -> float:
        """Calculate confidence score for key fob detection."""
        score = 0.0

        # Modulation type weight: 30%
        if features.modulation_type == "FSK":
            score += 0.3

        # Burst pattern weight: 25%
        if (
            self.detection_thresholds["min_burst_count"]
            <= features.burst_count
            <= self.detection_thresholds["max_burst_count"]
        ):
            score += 0.25

        # Timing pattern weight: 20%
        if features.inter_burst_intervals:
            avg_interval = np.mean(features.inter_burst_intervals)
            if 10e-3 <= avg_interval <= 20e-3:
                score += 0.2

        # Frequency characteristics weight: 15%
        if 20e3 <= features.frequency_deviation <= 50e3:
            score += 0.15

        # Signal quality weight: 10%
        if features.snr >= self.detection_thresholds["min_snr"]:
            score += 0.1

        return min(1.0, score)

    def _calculate_tpms_confidence(self, features: SignalFeatures) -> float:
        """Calculate confidence score for TPMS detection."""
        score = 0.0

        # Modulation type weight: 30%
        if features.modulation_type == "FSK":
            score += 0.3

        # Burst pattern weight: 25%
        if 1 <= features.burst_count <= 3:
            score += 0.25

        # Frequency characteristics weight: 25%
        if 10e3 <= features.frequency_deviation <= 30e3:
            score += 0.25

        # Signal quality weight: 20%
        if features.snr >= self.detection_thresholds["min_snr"]:
            score += 0.2

        return min(1.0, score)
