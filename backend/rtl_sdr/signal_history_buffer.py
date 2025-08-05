"""
signal_history_buffer.py

Signal history buffer for temporal analysis and replay detection.
Maintains a rolling buffer of detected signals for comparison and analysis.

This module provides the SignalHistoryBuffer class which:
- Stores recent signal detections with timestamps
- Enables temporal analysis for replay attack detection
- Provides efficient signal similarity comparison
- Manages memory usage with configurable buffer size

Example usage:
    buffer = SignalHistoryBuffer(max_size=1000, time_window=300)
    buffer.add_signal(detected_signal)
    recent_signals = buffer.get_recent_signals(60)  # Last 60 seconds
"""

import time
import threading
from typing import List, Dict, Any, Optional
from collections import deque
from dataclasses import dataclass
import numpy as np
import logging

logger = logging.getLogger(__name__)


@dataclass
class StoredSignal:
    """Container for stored signal with metadata."""

    signal_data: Dict[str, Any]
    timestamp: float
    signal_id: str
    signal_type: str
    features: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "signal_data": self.signal_data,
            "timestamp": self.timestamp,
            "signal_id": self.signal_id,
            "signal_type": self.signal_type,
            "features": self.features,
        }


class SignalHistoryBuffer:
    """
    Thread-safe signal history buffer for temporal analysis.

    This class maintains a rolling buffer of detected signals that can be used
    for replay attack detection, pattern analysis, and temporal correlation.
    """

    def __init__(self, max_size: int = 1000, time_window: float = 300.0):
        """
        Initialize the signal history buffer.

        Args:
            max_size: Maximum number of signals to store
            time_window: Time window in seconds for signal retention
        """
        self.max_size = max_size
        self.time_window = time_window
        self._buffer = deque(maxlen=max_size)
        self._lock = threading.RLock()
        self._signal_counter = 0

        logger.info(
            f"SignalHistoryBuffer initialized: max_size={max_size}, time_window={time_window}s"
        )

    def add_signal(self, signal_data: Dict[str, Any]) -> str:
        """
        Add a signal to the history buffer.

        Args:
            signal_data: Signal data dictionary

        Returns:
            Signal ID for the stored signal
        """
        with self._lock:
            self._signal_counter += 1
            signal_id = f"sig_{int(time.time())}_{self._signal_counter}"

            stored_signal = StoredSignal(
                signal_data=signal_data.copy(),
                timestamp=time.time(),
                signal_id=signal_id,
                signal_type=signal_data.get("signal_type", "unknown"),
                features=signal_data.get("features", {}),
            )

            self._buffer.append(stored_signal)

            # Clean old signals
            self._cleanup_old_signals()

            logger.debug(
                f"Added signal {signal_id} to buffer (buffer size: {len(self._buffer)})"
            )
            return signal_id

    def add_signals(self, signals: List[Dict[str, Any]]) -> List[str]:
        """
        Add multiple signals to the buffer.

        Args:
            signals: List of signal data dictionaries

        Returns:
            List of signal IDs for the stored signals
        """
        signal_ids = []
        for signal in signals:
            signal_id = self.add_signal(signal)
            signal_ids.append(signal_id)
        return signal_ids

    def get_recent_signals(
        self, time_window: Optional[float] = None
    ) -> List[StoredSignal]:
        """
        Get signals from the recent time window.

        Args:
            time_window: Time window in seconds (uses default if None)

        Returns:
            List of recent signals
        """
        if time_window is None:
            time_window = self.time_window

        current_time = time.time()
        cutoff_time = current_time - time_window

        with self._lock:
            recent_signals = [
                signal for signal in self._buffer if signal.timestamp >= cutoff_time
            ]

        logger.debug(
            f"Retrieved {len(recent_signals)} signals from last {time_window}s"
        )
        return recent_signals

    def get_signals_by_type(
        self, signal_type: str, time_window: Optional[float] = None
    ) -> List[StoredSignal]:
        """
        Get signals of a specific type from the recent time window.

        Args:
            signal_type: Type of signal to retrieve
            time_window: Time window in seconds (uses default if None)

        Returns:
            List of signals of the specified type
        """
        recent_signals = self.get_recent_signals(time_window)

        filtered_signals = [
            signal for signal in recent_signals if signal.signal_type == signal_type
        ]

        logger.debug(
            f"Retrieved {len(filtered_signals)} signals of type '{signal_type}'"
        )
        return filtered_signals

    def find_similar_signals(
        self,
        target_signal: Dict[str, Any],
        similarity_threshold: float = 0.8,
        time_window: Optional[float] = None,
    ) -> List[StoredSignal]:
        """
        Find signals similar to the target signal.

        Args:
            target_signal: Signal to compare against
            similarity_threshold: Minimum similarity score (0.0 to 1.0)
            time_window: Time window to search in seconds

        Returns:
            List of similar signals
        """
        recent_signals = self.get_recent_signals(time_window)
        similar_signals = []

        for stored_signal in recent_signals:
            similarity = self._calculate_signal_similarity(
                target_signal, stored_signal.signal_data
            )

            if similarity >= similarity_threshold:
                similar_signals.append(stored_signal)
                logger.debug(
                    f"Found similar signal {stored_signal.signal_id} with similarity {similarity:.3f}"
                )

        return similar_signals

    def _calculate_signal_similarity(
        self, signal1: Dict[str, Any], signal2: Dict[str, Any]
    ) -> float:
        """
        Calculate similarity between two signals.

        Args:
            signal1: First signal data
            signal2: Second signal data

        Returns:
            Similarity score between 0.0 and 1.0
        """
        similarity_score = 0.0
        comparison_count = 0

        # Compare signal features if available
        features1 = signal1.get("features", {})
        features2 = signal2.get("features", {})

        if features1 and features2:
            # Compare power spectrum if available
            if "power_spectrum" in features1 and "power_spectrum" in features2:
                power_sim = self._compare_power_spectra(
                    features1["power_spectrum"], features2["power_spectrum"]
                )
                similarity_score += power_sim * 0.4
                comparison_count += 1

            # Compare burst timing
            if "burst_timing" in features1 and "burst_timing" in features2:
                timing_sim = self._compare_burst_timing(
                    features1["burst_timing"], features2["burst_timing"]
                )
                similarity_score += timing_sim * 0.3
                comparison_count += 1

            # Compare frequency deviation
            if (
                "frequency_deviation" in features1
                and "frequency_deviation" in features2
            ):
                freq_sim = self._compare_frequency_deviation(
                    features1["frequency_deviation"], features2["frequency_deviation"]
                )
                similarity_score += freq_sim * 0.2
                comparison_count += 1

            # Compare signal bandwidth
            if "signal_bandwidth" in features1 and "signal_bandwidth" in features2:
                bw_sim = self._compare_bandwidth(
                    features1["signal_bandwidth"], features2["signal_bandwidth"]
                )
                similarity_score += bw_sim * 0.1
                comparison_count += 1

        # Fallback comparison using basic signal properties
        if comparison_count == 0:
            # Compare basic properties
            if "power_db" in signal1 and "power_db" in signal2:
                power_diff = abs(signal1["power_db"] - signal2["power_db"])
                power_sim = max(0, 1 - power_diff / 20)  # Normalize by 20dB range
                similarity_score += power_sim * 0.5
                comparison_count += 1

            if "peak_count" in signal1 and "peak_count" in signal2:
                peak_diff = abs(signal1["peak_count"] - signal2["peak_count"])
                peak_sim = max(0, 1 - peak_diff / 10)  # Normalize by 10 peaks
                similarity_score += peak_sim * 0.5
                comparison_count += 1

        if comparison_count > 0:
            return similarity_score / comparison_count
        else:
            return 0.0

    def _compare_power_spectra(
        self, spectrum1: List[float], spectrum2: List[float]
    ) -> float:
        """Compare two power spectra using correlation."""
        try:
            if len(spectrum1) != len(spectrum2):
                # Resample to same length
                min_len = min(len(spectrum1), len(spectrum2))
                spectrum1 = spectrum1[:min_len]
                spectrum2 = spectrum2[:min_len]

            if len(spectrum1) == 0:
                return 0.0

            # Calculate correlation coefficient
            correlation = np.corrcoef(spectrum1, spectrum2)[0, 1]

            # Handle NaN case
            if np.isnan(correlation):
                return 0.0

            # Convert to similarity (0 to 1)
            return max(0, correlation)

        except Exception as e:
            logger.warning(f"Error comparing power spectra: {e}")
            return 0.0

    def _compare_burst_timing(
        self, timing1: List[float], timing2: List[float]
    ) -> float:
        """Compare burst timing patterns."""
        try:
            if len(timing1) != len(timing2):
                return 0.0

            if len(timing1) == 0:
                return 1.0  # Both empty

            # Calculate timing differences
            timing_diffs = [abs(t1 - t2) for t1, t2 in zip(timing1, timing2)]
            avg_diff = np.mean(timing_diffs)

            # Convert to similarity (smaller differences = higher similarity)
            # Assume timing differences > 5ms indicate different patterns
            similarity = max(0, 1 - avg_diff / 0.005)

            return similarity

        except Exception as e:
            logger.warning(f"Error comparing burst timing: {e}")
            return 0.0

    def _compare_frequency_deviation(self, freq1: float, freq2: float) -> float:
        """Compare frequency deviations."""
        try:
            if freq1 == 0 and freq2 == 0:
                return 1.0

            max_freq = max(abs(freq1), abs(freq2))
            if max_freq == 0:
                return 1.0

            diff = abs(freq1 - freq2)
            similarity = max(0, 1 - diff / max_freq)

            return similarity

        except Exception as e:
            logger.warning(f"Error comparing frequency deviation: {e}")
            return 0.0

    def _compare_bandwidth(self, bw1: float, bw2: float) -> float:
        """Compare signal bandwidths."""
        try:
            if bw1 == 0 and bw2 == 0:
                return 1.0

            max_bw = max(bw1, bw2)
            if max_bw == 0:
                return 1.0

            diff = abs(bw1 - bw2)
            similarity = max(0, 1 - diff / max_bw)

            return similarity

        except Exception as e:
            logger.warning(f"Error comparing bandwidth: {e}")
            return 0.0

    def _cleanup_old_signals(self):
        """Remove signals older than the time window."""
        current_time = time.time()
        cutoff_time = current_time - self.time_window

        # Remove old signals from the front of the deque
        while self._buffer and self._buffer[0].timestamp < cutoff_time:
            removed_signal = self._buffer.popleft()
            logger.debug(f"Removed old signal {removed_signal.signal_id}")

    def get_buffer_stats(self) -> Dict[str, Any]:
        """Get buffer statistics."""
        with self._lock:
            current_time = time.time()

            if not self._buffer:
                return {
                    "total_signals": 0,
                    "buffer_size": 0,
                    "oldest_signal_age": 0,
                    "newest_signal_age": 0,
                    "signal_types": {},
                }

            oldest_age = current_time - self._buffer[0].timestamp
            newest_age = current_time - self._buffer[-1].timestamp

            # Count signal types
            signal_types = {}
            for signal in self._buffer:
                signal_type = signal.signal_type
                signal_types[signal_type] = signal_types.get(signal_type, 0) + 1

            return {
                "total_signals": len(self._buffer),
                "buffer_size": len(self._buffer),
                "oldest_signal_age": oldest_age,
                "newest_signal_age": newest_age,
                "signal_types": signal_types,
            }

    def clear_buffer(self):
        """Clear all signals from the buffer."""
        with self._lock:
            self._buffer.clear()
            logger.info("Signal history buffer cleared")

    def __len__(self) -> int:
        """Return the number of signals in the buffer."""
        return len(self._buffer)

    def __bool__(self) -> bool:
        """Return True if buffer contains signals."""
        return len(self._buffer) > 0
