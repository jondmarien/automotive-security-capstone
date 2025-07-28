# Enhanced Signal Processing Architecture

## Overview

The Enhanced Signal Processing system provides advanced automotive RF signal analysis capabilities, including sophisticated threat detection, replay attack analysis, and temporal correlation. This system builds upon the existing signal processing infrastructure while maintaining full backward compatibility.

## Architecture Components

### 1. AutomotiveSignalAnalyzer (`automotive_signal_analyzer.py`)

The core signal analysis engine that processes IQ samples and extracts automotive-specific features.

#### Key Features
- **Real-time IQ Analysis**: Advanced FFT-based power spectrum computation
- **Key Fob Detection**: FSK pattern recognition with timing analysis
- **TPMS Signal Detection**: Tire pressure monitoring system identification
- **Burst Pattern Analysis**: Sophisticated burst timing and interval detection
- **Modulation Classification**: Automatic FSK/ASK/Unknown modulation detection
- **Confidence Scoring**: Multi-factor confidence calculation

#### Signal Features Extracted
```python
@dataclass
class SignalFeatures:
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
```

#### Detection Algorithms

##### Key Fob Detection
- **Modulation**: FSK detection with frequency deviation analysis
- **Burst Pattern**: 3-8 bursts with 10-20ms intervals
- **Frequency Deviation**: 20-50 kHz typical for automotive key fobs
- **Bandwidth**: 20-80 kHz signal bandwidth
- **Confidence Calculation**: Multi-factor scoring (modulation 30%, burst pattern 25%, timing 20%, frequency 15%, signal quality 10%)

##### TPMS Detection
- **Modulation**: FSK with lower frequency deviation (10-30 kHz)
- **Burst Pattern**: 1-3 longer bursts (5-15ms duration)
- **Transmission Interval**: 30-300 seconds between transmissions
- **Bandwidth**: 10-40 kHz signal bandwidth
- **Data Rate**: 9.6-19.2 kbps typical

### 2. Signal History Buffer (`signal_history_buffer.py`)

Thread-safe signal storage system for temporal analysis and replay detection.

#### Key Features
- **Rolling Buffer**: Configurable size (default: 1000 signals)
- **Time Window**: Configurable retention (default: 5 minutes)
- **Thread Safety**: RLock-based concurrent access
- **Signal Similarity**: Advanced correlation analysis
- **Memory Management**: Automatic cleanup of old signals

#### Signal Storage
```python
@dataclass
class StoredSignal:
    signal_data: Dict[str, Any]
    timestamp: float
    signal_id: str
    signal_type: str
    features: Dict[str, Any]
```

#### Similarity Analysis
- **Power Spectrum Correlation**: 40% weight in similarity calculation
- **Burst Timing Comparison**: 30% weight
- **Frequency Deviation**: 20% weight
- **Signal Bandwidth**: 10% weight

### 3. Enhanced Signal Processing Bridge (`enhanced_signal_bridge.py`)

Main orchestration component that integrates all enhanced processing capabilities.

#### Key Components

##### ThreatDetectionEngine
- **Replay Attack Detection**: Signal similarity analysis with temporal correlation
- **Jamming Detection**: Broadband interference and noise floor analysis
- **Brute Force Detection**: Rate-based attack pattern recognition
- **Threat Classification**: Automated BENIGN/SUSPICIOUS/MALICIOUS classification

##### ReplayAttackDetector
- **Similarity Threshold**: 95% similarity for replay detection
- **Time Window**: 5-minute analysis window
- **Timing Characteristics**: 1 second to 5 minutes typical replay timing
- **Confidence Scoring**: Signal similarity (60%), timing match (30%), frequency match (10%)

##### JammingDetector
- **Bandwidth Analysis**: >100 kHz indicates broadband jamming
- **Noise Floor**: RSSI > -80 dBm with elevated noise
- **Burst Analysis**: Continuous transmission or excessive burst count
- **Modulation Analysis**: Unrecognized patterns indicate jamming

##### BruteForceDetector
- **Rate Threshold**: >10 signals per minute of same type
- **Time Window**: 60-second sliding window
- **Pattern Analysis**: Inter-signal interval consistency
- **Confidence Scoring**: Based on rate excess above threshold

## Integration with Existing System

### Backward Compatibility

The enhanced system maintains full backward compatibility through the existing `SignalProcessingBridge` class:

```python
# Legacy mode (default)
bridge = SignalProcessingBridge(rtl_server_manager)

# Enhanced mode
bridge = SignalProcessingBridge(rtl_server_manager, enhanced_mode=True)
```

### Configuration Options

```python
# AutomotiveSignalAnalyzer configuration
analyzer = AutomotiveSignalAnalyzer(sample_rate=2048000)

# Detection thresholds
detection_thresholds = {
    'min_snr': 10.0,  # dB
    'min_burst_count': 3,
    'max_burst_count': 8,
    'min_confidence': 0.6,
    'key_fob_bandwidth': (10e3, 100e3),  # Hz
    'tpms_bandwidth': (5e3, 50e3),  # Hz
}

# Signal history buffer configuration
signal_history = SignalHistoryBuffer(max_size=1000, time_window=300.0)
```

## Performance Characteristics

### Real-time Processing
- **Latency Target**: <100ms from signal capture to threat detection
- **Throughput**: Handles 3.2 MS/s sample rate from RTL-SDR
- **Memory Usage**: Efficient buffer management for continuous operation
- **CPU Usage**: Optimized FFT operations and pattern matching

### Test Results
- **Signal Processing**: <1 second for 1-second signal analysis
- **Threat Detection**: Real-time classification with <100ms latency
- **Memory Usage**: Stable memory footprint with automatic cleanup
- **Test Coverage**: 45 comprehensive tests with 100% pass rate

## Usage Examples

### Basic Enhanced Processing
```python
from rtl_sdr.enhanced_signal_bridge import EnhancedSignalProcessingBridge

# Initialize enhanced bridge
bridge = EnhancedSignalProcessingBridge(rtl_server_manager)

# Start processing
await bridge.start_signal_processing()
```

### Signal Analysis
```python
from rtl_sdr.automotive_signal_analyzer import AutomotiveSignalAnalyzer

# Initialize analyzer
analyzer = AutomotiveSignalAnalyzer(sample_rate=2048000)

# Extract features
features = analyzer.extract_features(complex_samples)

# Detect automotive patterns
detected_signals = analyzer.detect_automotive_patterns(features)
```

### Threat Detection
```python
from rtl_sdr.enhanced_signal_bridge import ThreatDetectionEngine
from rtl_sdr.signal_history_buffer import SignalHistoryBuffer

# Initialize components
signal_history = SignalHistoryBuffer()
threat_detector = ThreatDetectionEngine(signal_history)

# Analyze for threats
threat_analysis = threat_detector.analyze_threat(detected_signal)
```

## Future Enhancements

### Machine Learning Integration
- **Pattern Recognition**: ML-based signal classification
- **Anomaly Detection**: Unsupervised learning for unknown threats
- **Adaptive Thresholds**: Dynamic threshold adjustment based on environment

### Advanced Signal Processing
- **Multi-frequency Analysis**: Simultaneous monitoring of multiple bands
- **Direction Finding**: Signal source localization
- **Protocol Decoding**: Deep packet inspection for automotive protocols

### Performance Optimization
- **GPU Acceleration**: CUDA-based FFT processing
- **Distributed Processing**: Multi-node signal analysis
- **Real-time Visualization**: Live spectrum analysis display

## Dependencies

### Required Libraries
- **NumPy**: Core numerical computing and FFT operations
- **SciPy**: Advanced signal processing functions and peak detection
- **Threading**: Thread-safe signal history management
- **Asyncio**: Asynchronous processing and event handling
- **Dataclasses**: Structured data containers
- **Typing**: Type hints for better code maintainability

### Installation
```bash
# Install enhanced dependencies
pip install scipy>=1.11.0

# Or using UV
uv pip install scipy>=1.11.0
```

## Testing

### Test Coverage
- **AutomotiveSignalAnalyzer**: 24 comprehensive tests
- **Enhanced Signal Bridge**: 21 tests covering all components
- **Signal History Buffer**: Thread safety and performance tests
- **Threat Detection**: Replay, jamming, and brute force detection tests

### Running Tests
```bash
# Run all enhanced signal processing tests
pytest tests/test_automotive_signal_analyzer.py tests/test_enhanced_signal_bridge.py -v

# Run with coverage
pytest tests/test_automotive_signal_analyzer.py tests/test_enhanced_signal_bridge.py --cov=rtl_sdr --cov-report=html
```

## Troubleshooting

### Common Issues
1. **SciPy Import Error**: Ensure SciPy is installed (`pip install scipy>=1.11.0`)
2. **Memory Usage**: Adjust signal history buffer size for memory-constrained systems
3. **Performance**: Reduce sample rate or buffer size for slower systems
4. **Thread Safety**: Ensure proper cleanup when stopping processing

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Enhanced processing with debug info
bridge = EnhancedSignalProcessingBridge(rtl_server_manager)
stats = bridge.get_processing_stats()
print(f"Processing stats: {stats}")
```

This enhanced signal processing system provides a solid foundation for advanced automotive security monitoring while maintaining the flexibility and performance required for real-time threat detection.