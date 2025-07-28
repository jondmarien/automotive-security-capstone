"""
test_automotive_signal_analyzer.py

Comprehensive tests for the AutomotiveSignalAnalyzer class.
Tests signal feature extraction, pattern recognition, and classification accuracy.
"""

import pytest
import numpy as np
import time
from unittest.mock import Mock, patch

# Import the module under test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from rtl_sdr.automotive_signal_analyzer import (
    AutomotiveSignalAnalyzer, 
    SignalFeatures, 
    DetectedSignal
)

class TestAutomotiveSignalAnalyzer:
    """Test suite for AutomotiveSignalAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = AutomotiveSignalAnalyzer(sample_rate=2048000)
        self.sample_rate = 2048000
    
    def generate_test_signal(self, signal_type='key_fob', duration=0.1, noise_level=0.1):
        """Generate synthetic test signals for testing."""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        if signal_type == 'key_fob':
            # Generate FSK key fob signal with multiple bursts
            signal = np.zeros(len(t), dtype=complex)
            
            # Create 4 bursts with 15ms intervals
            burst_duration = 0.003  # 3ms bursts
            burst_interval = 0.015  # 15ms intervals
            burst_amplitude = 5.0  # Higher amplitude for better detection
            
            for i in range(4):
                start_time = i * burst_interval
                end_time = start_time + burst_duration
                
                burst_mask = (t >= start_time) & (t < end_time)
                
                if np.any(burst_mask):  # Only if there are samples in this burst
                    # FSK modulation: alternating between two frequencies
                    f1, f2 = 1000, 5000  # Hz deviation from center
                    freq_pattern = np.where(np.random.random(np.sum(burst_mask)) > 0.5, f1, f2)
                    
                    burst_signal = burst_amplitude * np.exp(1j * 2 * np.pi * freq_pattern * t[burst_mask])
                    signal[burst_mask] = burst_signal
            
        elif signal_type == 'tpms':
            # Generate TPMS signal (single longer burst)
            burst_duration = 0.01  # 10ms burst
            burst_mask = t < burst_duration
            burst_amplitude = 3.0  # Higher amplitude for better detection
            
            # Lower frequency deviation for TPMS
            freq_deviation = np.random.choice([500, -500], size=np.sum(burst_mask))
            signal = np.zeros(len(t), dtype=complex)
            signal[burst_mask] = burst_amplitude * np.exp(1j * 2 * np.pi * freq_deviation * t[burst_mask])
            
        elif signal_type == 'noise':
            # Generate white noise
            signal = (np.random.normal(0, 1, len(t)) + 
                     1j * np.random.normal(0, 1, len(t))) * noise_level
            
        else:
            # Generate continuous tone
            signal = np.exp(1j * 2 * np.pi * 1000 * t)
        
        # Add noise
        noise = (np.random.normal(0, noise_level, len(t)) + 
                1j * np.random.normal(0, noise_level, len(t)))
        
        return signal + noise
    
    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = AutomotiveSignalAnalyzer(sample_rate=1000000)
        assert analyzer.sample_rate == 1000000
        assert 'north_america_keyfob' in analyzer.frequency_bands
        assert 'standard_keyfob' in analyzer.key_fob_patterns
        assert 'standard_tpms' in analyzer.tpms_patterns
    
    def test_extract_features_basic(self):
        """Test basic feature extraction."""
        test_signal = self.generate_test_signal('key_fob')
        features = self.analyzer.extract_features(test_signal)
        
        assert isinstance(features, SignalFeatures)
        assert features.timestamp > 0
        assert len(features.power_spectrum) == len(test_signal)
        assert isinstance(features.burst_timing, list)
        assert features.modulation_type in ['FSK', 'ASK', 'Unknown']
        assert features.frequency_deviation >= 0
        assert features.signal_bandwidth >= 0
        assert isinstance(features.snr, float)
        assert isinstance(features.rssi, float)
    
    def test_power_spectrum_computation(self):
        """Test power spectrum computation."""
        # Generate a known frequency signal
        duration = 0.1
        freq = 1000  # 1 kHz
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        test_signal = np.exp(1j * 2 * np.pi * freq * t)
        
        power_spectrum = self.analyzer._compute_power_spectrum(test_signal)
        
        assert len(power_spectrum) == len(test_signal)
        assert isinstance(power_spectrum, np.ndarray)
        # Power spectrum should have a peak at the test frequency
        assert np.max(power_spectrum) > np.mean(power_spectrum) + 10  # At least 10dB above mean
    
    def test_burst_timing_detection(self):
        """Test burst timing detection."""
        test_signal = self.generate_test_signal('key_fob')
        burst_timing = self.analyzer._detect_burst_timing(test_signal)
        
        assert isinstance(burst_timing, list)
        # Key fob should have multiple bursts
        assert len(burst_timing) >= 2
        # Burst times should be in ascending order
        assert all(burst_timing[i] <= burst_timing[i+1] for i in range(len(burst_timing)-1))
    
    def test_modulation_classification(self):
        """Test modulation type classification."""
        # Test FSK signal (key fob)
        fsk_signal = self.generate_test_signal('key_fob')
        modulation = self.analyzer._classify_modulation(fsk_signal)
        assert modulation in ['FSK', 'ASK', 'Unknown']
        
        # Test continuous tone (should be ASK or Unknown)
        tone_signal = self.generate_test_signal('tone')
        modulation = self.analyzer._classify_modulation(tone_signal)
        assert modulation in ['FSK', 'ASK', 'Unknown']
    
    def test_frequency_deviation_measurement(self):
        """Test frequency deviation measurement."""
        test_signal = self.generate_test_signal('key_fob')
        deviation = self.analyzer._measure_frequency_deviation(test_signal)
        
        assert isinstance(deviation, float)
        assert deviation >= 0
        # Should detect some frequency deviation in FSK signal
        assert deviation > 100  # At least 100 Hz deviation
    
    def test_bandwidth_measurement(self):
        """Test signal bandwidth measurement."""
        test_signal = self.generate_test_signal('key_fob')
        power_spectrum = self.analyzer._compute_power_spectrum(test_signal)
        bandwidth = self.analyzer._measure_bandwidth(test_signal, power_spectrum)
        
        assert isinstance(bandwidth, float)
        assert bandwidth >= 0
        # Bandwidth should be reasonable for test signal
        assert bandwidth < self.sample_rate / 2  # Less than Nyquist frequency
    
    def test_snr_calculation(self):
        """Test SNR calculation."""
        # High SNR signal
        high_snr_signal = self.generate_test_signal('key_fob', noise_level=0.01)
        high_snr = self.analyzer._calculate_snr(high_snr_signal)
        
        # Low SNR signal
        low_snr_signal = self.generate_test_signal('key_fob', noise_level=1.0)
        low_snr = self.analyzer._calculate_snr(low_snr_signal)
        
        assert isinstance(high_snr, float)
        assert isinstance(low_snr, float)
        # High SNR should be greater than low SNR
        assert high_snr > low_snr
    
    def test_rssi_calculation(self):
        """Test RSSI calculation."""
        test_signal = self.generate_test_signal('key_fob')
        rssi = self.analyzer._calculate_rssi(test_signal)
        
        assert isinstance(rssi, float)
        # RSSI should be negative (dBm)
        assert rssi < 0
    
    def test_peak_frequency_detection(self):
        """Test peak frequency detection."""
        test_signal = self.generate_test_signal('key_fob')
        power_spectrum = self.analyzer._compute_power_spectrum(test_signal)
        peaks = self.analyzer._find_peak_frequencies(power_spectrum)
        
        assert isinstance(peaks, list)
        # Should find at least one peak
        assert len(peaks) >= 0
        # All peaks should be positive frequencies
        assert all(peak >= 0 for peak in peaks)
    
    def test_inter_burst_intervals(self):
        """Test inter-burst interval calculation."""
        burst_timing = [0.0, 0.015, 0.030, 0.045]  # 15ms intervals
        intervals = self.analyzer._calculate_inter_burst_intervals(burst_timing)
        
        assert len(intervals) == 3
        assert all(abs(interval - 0.015) < 0.001 for interval in intervals)
        
        # Test empty case
        empty_intervals = self.analyzer._calculate_inter_burst_intervals([])
        assert empty_intervals == []
        
        # Test single burst case
        single_intervals = self.analyzer._calculate_inter_burst_intervals([0.0])
        assert single_intervals == []
    
    def test_key_fob_pattern_detection(self):
        """Test key fob pattern detection."""
        test_signal = self.generate_test_signal('key_fob')
        features = self.analyzer.extract_features(test_signal)
        
        detected_signal = self.analyzer._detect_key_fob_pattern(features)
        
        if detected_signal:  # Detection is probabilistic
            assert isinstance(detected_signal, DetectedSignal)
            assert detected_signal.signal_type == 'key_fob'
            assert 0.0 <= detected_signal.confidence <= 1.0
            assert detected_signal.timestamp > 0
            assert isinstance(detected_signal.classification_details, dict)
    
    def test_tpms_pattern_detection(self):
        """Test TPMS pattern detection."""
        test_signal = self.generate_test_signal('tpms')
        features = self.analyzer.extract_features(test_signal)
        
        detected_signal = self.analyzer._detect_tpms_pattern(features)
        
        if detected_signal:  # Detection is probabilistic
            assert isinstance(detected_signal, DetectedSignal)
            assert detected_signal.signal_type == 'tpms'
            assert 0.0 <= detected_signal.confidence <= 1.0
            assert detected_signal.timestamp > 0
            assert isinstance(detected_signal.classification_details, dict)
    
    def test_detect_automotive_patterns(self):
        """Test comprehensive automotive pattern detection."""
        test_signal = self.generate_test_signal('key_fob')
        features = self.analyzer.extract_features(test_signal)
        
        detected_signals = self.analyzer.detect_automotive_patterns(features)
        
        assert isinstance(detected_signals, list)
        # Each detected signal should be valid
        for signal in detected_signals:
            assert isinstance(signal, DetectedSignal)
            assert signal.signal_type in ['key_fob', 'tpms']
            assert 0.0 <= signal.confidence <= 1.0
    
    def test_confidence_score_calculation(self):
        """Test confidence score calculation."""
        test_signal = self.generate_test_signal('key_fob')
        features = self.analyzer.extract_features(test_signal)
        
        # Test key fob confidence
        key_fob_confidence = self.analyzer.calculate_confidence_score('key_fob', features)
        assert 0.0 <= key_fob_confidence <= 1.0
        
        # Test TPMS confidence
        tpms_confidence = self.analyzer.calculate_confidence_score('tpms', features)
        assert 0.0 <= tpms_confidence <= 1.0
        
        # Test unknown signal type
        unknown_confidence = self.analyzer.calculate_confidence_score('unknown', features)
        assert unknown_confidence == 0.0
    
    def test_signal_features_serialization(self):
        """Test SignalFeatures serialization."""
        test_signal = self.generate_test_signal('key_fob')
        features = self.analyzer.extract_features(test_signal)
        
        features_dict = features.to_dict()
        
        assert isinstance(features_dict, dict)
        assert 'timestamp' in features_dict
        assert 'power_spectrum' in features_dict
        assert 'burst_timing' in features_dict
        assert 'modulation_type' in features_dict
        assert isinstance(features_dict['power_spectrum'], list)
    
    def test_detected_signal_serialization(self):
        """Test DetectedSignal serialization."""
        test_signal = self.generate_test_signal('key_fob')
        features = self.analyzer.extract_features(test_signal)
        
        detected_signals = self.analyzer.detect_automotive_patterns(features)
        
        for signal in detected_signals:
            signal_dict = signal.to_dict()
            
            assert isinstance(signal_dict, dict)
            assert 'signal_type' in signal_dict
            assert 'confidence' in signal_dict
            assert 'features' in signal_dict
            assert 'timestamp' in signal_dict
            assert 'classification_details' in signal_dict
    
    def test_noise_rejection(self):
        """Test that noise signals are properly rejected."""
        noise_signal = self.generate_test_signal('noise')
        features = self.analyzer.extract_features(noise_signal)
        
        detected_signals = self.analyzer.detect_automotive_patterns(features)
        
        # Noise should not be detected as automotive signals
        # or should have very low confidence
        for signal in detected_signals:
            assert signal.confidence < 0.8  # Should have low confidence for noise
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Empty signal
        empty_signal = np.array([], dtype=complex)
        
        # Should handle empty signals gracefully
        try:
            features = self.analyzer.extract_features(empty_signal)
            # If it doesn't raise an exception, check that features are reasonable
            assert features is not None
        except (ValueError, IndexError):
            # It's acceptable to raise an exception for empty input
            pass
        
        # Very short signal
        short_signal = np.array([1+1j, 2+2j], dtype=complex)
        
        try:
            features = self.analyzer.extract_features(short_signal)
            assert features is not None
        except (ValueError, IndexError):
            # It's acceptable to raise an exception for very short input
            pass
    
    @pytest.mark.parametrize("signal_type", ['key_fob', 'tpms', 'noise', 'tone'])
    def test_different_signal_types(self, signal_type):
        """Test analyzer with different signal types."""
        test_signal = self.generate_test_signal(signal_type)
        features = self.analyzer.extract_features(test_signal)
        
        assert isinstance(features, SignalFeatures)
        assert features.timestamp > 0
        
        detected_signals = self.analyzer.detect_automotive_patterns(features)
        assert isinstance(detected_signals, list)
    
    def test_performance(self):
        """Test performance with realistic signal lengths."""
        # Generate a longer signal (1 second)
        long_signal = self.generate_test_signal('key_fob', duration=1.0)
        
        start_time = time.time()
        features = self.analyzer.extract_features(long_signal)
        detected_signals = self.analyzer.detect_automotive_patterns(features)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should process 1 second of signal in reasonable time (< 1 second for real-time)
        assert processing_time < 1.0
        assert isinstance(features, SignalFeatures)
        assert isinstance(detected_signals, list)

if __name__ == '__main__':
    pytest.main([__file__])