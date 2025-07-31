# Detection Module API Reference

This document provides comprehensive API documentation for the detection module components, including the new JammingDetector class.

## Overview

The detection module provides advanced threat detection capabilities for automotive RF signals, including replay attack detection, jamming detection, and brute force attack detection.

## Core Classes

### ThreatLevel (Enum)

Enumeration defining threat classification levels.

```python
from detection.threat_levels import ThreatLevel

class ThreatLevel(Enum):
    BENIGN = auto()      # Normal automotive RF activity
    SUSPICIOUS = auto()  # Unusual patterns requiring investigation
    MALICIOUS = auto()   # Clear attack signatures detected
```

### JammingDetector

Advanced jamming detector for RF interference patterns and denial-of-service attacks.

#### Constructor

```python
def __init__(self, noise_threshold: float = 10.0, interference_threshold: float = 0.8)
```

**Parameters:**

- `noise_threshold` (float): Minimum noise floor elevation (dB) to consider jamming. Default: 10.0
- `interference_threshold` (float): Minimum interference ratio to classify as jamming. Default: 0.8

#### Methods

##### check_jamming()

Check if current signal conditions indicate jamming attack.

```python
def check_jamming(self, signal: Dict[str, Any], signal_history: List[Dict[str, Any]]) -> Dict[str, Any]
```

**Parameters:**

- `signal` (Dict[str, Any]): Current signal to analyze
- `signal_history` (List[Dict[str, Any]]): List of recent signals for baseline comparison

**Returns:**

- Dictionary containing jamming detection results and evidence

**Return Structure:**

```python
{
    'is_jamming': bool,           # True if jamming detected
    'confidence': float,          # Confidence score (0.0 to 1.0)
    'evidence': JammingEvidence,  # Technical evidence object (if jamming detected)
    'threat_level': ThreatLevel,  # Threat classification
    'description': str            # Human-readable description
}
```

#### Private Methods

##### \_analyze_noise_floor()

Analyze noise floor elevation compared to baseline.

```python
def _analyze_noise_floor(self, signal: Dict[str, Any], signal_history: List[Dict[str, Any]]) -> Dict[str, Any]
```

##### \_detect_broadband_interference()

Detect broadband interference patterns using spectral flatness analysis.

```python
def _detect_broadband_interference(self, signal: Dict[str, Any]) -> bool
```

**Parameters:**

- `signal` (Dict[str, Any]): Signal containing power spectrum data

**Returns:**

- `bool`: True if broadband interference detected (spectral flatness > 0.5), False otherwise

**Algorithm:**

- Calculates spectral flatness using geometric mean / arithmetic mean ratio
- High spectral flatness (> 0.5) indicates broadband interference typical of jamming
- Returns proper Python boolean for consistent type handling

##### \_identify_jamming_pattern()

Identify the type of jamming pattern from four supported types.

```python
def _identify_jamming_pattern(self, signal: Dict[str, Any], signal_history: List[Dict[str, Any]]) -> Dict[str, Any]
```

**Supported Jamming Patterns:**

- **Continuous Jamming**: Sustained high power with low variance
- **Pulse Jamming**: Periodic high-power bursts with regular timing
- **Sweep Jamming**: Systematic frequency progression
- **Spot Jamming**: Narrow-band high power interference

##### \_detect_spot_jamming()

Detect spot jamming patterns (narrow-band interference).

```python
def _detect_spot_jamming(self, signal: Dict[str, Any], signal_history: List[Dict[str, Any]]) -> Dict[str, Any]
```

**Parameters:**

- `signal` (Dict[str, Any]): Signal containing power spectrum data
- `signal_history` (List[Dict[str, Any]]): Historical signals (not used in current implementation)

**Returns:**

- Dictionary containing spot jamming detection results

**Algorithm:**

- Calculates spectral peak characteristics using power spectrum data
- Computes peak-to-average ratio using maximum power / mean power
- **Detection Thresholds** (Updated for improved accuracy):
  - Peak-to-average ratio > 10.0 (increased from 5.0 for reduced false positives)
  - Minimum absolute power > 2.0 (new threshold to avoid noise-based false positives)
- High peak-to-average ratio indicates narrow-band interference typical of spot jamming
- Returns confidence score and estimated peak frequency

##### \_calculate_jamming_confidence()

Calculate overall jamming confidence score using weighted factors.

```python
def _calculate_jamming_confidence(self, noise_analysis: Dict[str, Any],
                                broadband_interference: bool,
                                jamming_pattern: Dict[str, Any]) -> float
```

**Confidence Factors:**

- Noise floor elevation: 30% weight
- Broadband interference: 20% weight
- Pattern detection: 50% weight

### JammingEvidence (Dataclass)

Evidence collected for jamming attack detection.

```python
@dataclass
class JammingEvidence:
    noise_floor_elevation: float        # Noise floor elevation in dB
    broadband_interference: bool        # True if broadband interference detected
    jamming_pattern_type: str          # Type of jamming pattern detected
    affected_frequencies: List[float]   # List of affected frequency ranges
    interference_duration: float       # Duration of interference in seconds
    signal_to_noise_degradation: float # SNR degradation in dB
    jamming_confidence: float          # Overall confidence score
```

### ReplayAttackDetector

Advanced replay attack detector using signal similarity analysis.

#### Constructor

```python
def __init__(self, similarity_threshold: float = 0.95, time_window: int = 300)
```

**Parameters:**

- `similarity_threshold` (float): Minimum similarity score to consider signals identical. Default: 0.95
- `time_window` (int): Time window in seconds to check for replay attacks. Default: 300

#### Methods

##### check_replay()

Check if a signal is a replay attack by comparing with recent signals.

```python
def check_replay(self, signal: Dict[str, Any], signal_history: List[Dict[str, Any]]) -> Dict[str, Any]
```

**Parameters:**

- `signal` (Dict[str, Any]): Current signal to analyze
- `signal_history` (List[Dict[str, Any]]): List of recent signals for comparison

**Returns:**

- Dictionary containing replay detection results and evidence

### ReplayEvidence (Dataclass)

Evidence collected for replay attack detection.

```python
@dataclass
class ReplayEvidence:
    original_timestamp: float          # Timestamp of original signal
    replay_timestamp: float            # Timestamp of replayed signal
    signal_similarity: float           # Overall similarity score
    timing_anomaly: Dict[str, Any]     # Timing anomaly analysis
    power_spectrum_correlation: float  # Power spectrum correlation coefficient
    burst_timing_similarity: float     # Burst timing pattern similarity
    frequency_deviation: float         # Frequency deviation between signals
```

## Usage Examples

### Basic Jamming Detection

```python
from detection.jamming_detector import JammingDetector
from detection.threat_levels import ThreatLevel

# Initialize detector
detector = JammingDetector(noise_threshold=10.0, interference_threshold=0.8)

# Analyze signal for jamming
signal = {
    'frequency': 433920000,
    'timestamp': time.time(),
    'features': {
        'rssi': -30.0,
        'noise_floor': -85.0,
        'power_spectrum': [1.2, 1.5, 2.1, 1.8, 1.3],
        'snr': 15.0
    }
}

signal_history = []  # List of recent signals

result = detector.check_jamming(signal, signal_history)

if result['is_jamming']:
    print(f"Jamming detected: {result['description']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Threat Level: {result['threat_level']}")

    evidence = result['evidence']
    print(f"Pattern Type: {evidence.jamming_pattern_type}")
    print(f"Noise Elevation: {evidence.noise_floor_elevation:.1f} dB")
```

### Advanced Replay Detection

```python
from detection.replay_attack_detector import ReplayAttackDetector

# Initialize detector
detector = ReplayAttackDetector(similarity_threshold=0.95, time_window=300)

# Check for replay attack
result = detector.check_replay(current_signal, signal_history)

if result['is_replay']:
    evidence = result['evidence']
    print(f"Replay attack detected!")
    print(f"Original signal: {evidence.original_timestamp}")
    print(f"Replay signal: {evidence.replay_timestamp}")
    print(f"Similarity: {evidence.signal_similarity:.2%}")
```

## Signal Data Format

### Expected Signal Structure

```python
signal = {
    'frequency': float,           # Signal frequency in Hz
    'timestamp': float,           # Unix timestamp (REQUIRED for temporal analysis)
    'sample_rate': int,          # Sample rate in Hz (optional)
    'features': {
        'rssi': float,           # Received signal strength (dBm)
        'snr': float,            # Signal-to-noise ratio (dB)
        'noise_floor': float,    # Noise floor level (dBm)
        'power_spectrum': List[float],  # Power spectrum data
        'burst_timing': List[float],    # Burst timing intervals
        'modulation_type': str,  # Detected modulation type
        'bandwidth': float       # Signal bandwidth (Hz)
    }
}
```

### Signal Data Requirements

**Critical for Accurate Detection:**

- **Timestamp Precision**: The `timestamp` field must contain accurate Unix timestamps for proper temporal analysis. Jamming detection relies on chronological signal ordering to establish noise floor baselines.
- **Signal History Ordering**: Provide signal history in chronological order (oldest to newest) for optimal baseline calculation.
- **Minimum History**: For reliable jamming detection, maintain at least 30-60 seconds of signal history (typically 50+ signals) to establish stable noise floor baselines.
- **Frequency Consistency**: Signals used for baseline comparison should be within ±1 MHz of the target frequency for accurate noise floor analysis.

## Error Handling

All detection methods include comprehensive error handling:

- **Invalid Input**: Methods validate input parameters and return safe defaults
- **Missing Data**: Graceful handling of missing signal features
- **Numerical Errors**: Protection against division by zero and invalid calculations
- **Memory Management**: Efficient handling of signal history buffers

## Performance Considerations

### Computational Complexity

- **Jamming Detection**: O(n) where n is signal history size
- **Replay Detection**: O(n²) for similarity comparison in worst case
- **Memory Usage**: Configurable signal history buffer size
- **Real-time Processing**: Optimized for <100ms processing latency

### Optimization Tips

1. **Adjust Buffer Sizes**: Reduce signal history size for memory-constrained systems
2. **Threshold Tuning**: Adjust detection thresholds based on environment
3. **Parallel Processing**: Use separate detector instances for concurrent analysis
4. **Caching**: Cache baseline noise calculations for improved performance

## Integration Notes

### Thread Safety

- JammingDetector and ReplayAttackDetector are thread-safe for read operations
- Signal history buffers should use appropriate locking for concurrent access
- Evidence objects are immutable after creation

### Configuration

Detectors can be configured through constructor parameters or runtime methods:

```python
# Runtime configuration
detector.noise_threshold = 15.0  # Adjust sensitivity
detector.interference_threshold = 0.7  # Lower threshold for more detections
```

### Logging

All detectors support standard Python logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Detector operations will log debug information
result = detector.check_jamming(signal, signal_history)
```

This API provides comprehensive threat detection capabilities while maintaining high performance and reliability for real-time automotive security monitoring.
