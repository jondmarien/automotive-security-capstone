# Code Snippets for Final Report

This document contains key code snippets from the automotive security capstone project with file references for screenshot purposes.

## 1. Signal Processing and Threshold Implementation

### Signal Detection Threshold (-60dBm)
**File**: `backend/rtl_sdr/signal_bridge.py` (Line 88)

```python
class SignalBridge:
    def __init__(self):
        self.processing_active = False
        self.signal_buffer = []
        self.detection_threshold = -60  # dBm threshold for signal detection
        self._last_cooldown_log_time = 0
        self._last_burst_time = 0
```

### Context-Aware Signal Filtering
**File**: `backend/detection/jamming_detector.py` (Lines 382-386)

```python
# Sweep jamming detection with context-aware thresholds
mean_power = np.mean(powers)

if directional_consistency > 0.6 and mean_power > -40:  # 60% consistency, -40 dBm threshold
    sweep_rate = abs(np.mean(freq_changes)) / 1e6  # MHz per signal
    confidence = min(1.0, directional_consistency * (mean_power + 60) / 60)
```

### Signal Quality Assessment
**File**: `backend/cli_dashboard_detection_adapter.py` (Lines 268-271)

```python
def generate_key_fob_event():
    signal_quality = random.uniform(0.70, 0.98)  # Good quality for legitimate key fob
    snr = random.uniform(15, 30)  # Good SNR for legitimate key fob (dB)
    power_db = random.uniform(-60, -40)  # Typical power level for key fob (dBm)
    
    # Generate burst pattern based on modulation
```

## 2. Automotive Signal Analysis

### FSK Detection Algorithm
**File**: `backend/rtl_sdr/automotive_signal_analyzer.py` (Lines 89-110)

```python
def detect_fsk_characteristics(self, signal_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
    """
    Detect FSK (Frequency Shift Keying) characteristics in automotive signals.
    Key fobs and TPMS sensors commonly use FSK modulation.
    """
    try:
        # Compute instantaneous frequency using phase derivative
        analytic_signal = hilbert(signal_data)
        instantaneous_phase = np.unwrap(np.angle(analytic_signal))
        instantaneous_freq = np.diff(instantaneous_phase) / (2.0 * np.pi) * sample_rate
        
        # Detect frequency shifts (FSK characteristics)
        freq_std = np.std(instantaneous_freq)
        freq_range = np.ptp(instantaneous_freq)  # Peak-to-peak range
        
        # FSK signals show distinct frequency levels
        fsk_detected = freq_std > 1000 and freq_range > 5000  # Hz thresholds
        
        return {
            'fsk_detected': fsk_detected,
            'frequency_std': float(freq_std),
            'frequency_range': float(freq_range),
            'confidence': min(1.0, freq_std / 10000.0)  # Normalize confidence
        }
    except Exception as e:
        self.logger.error(f"FSK detection failed: {e}")
        return {'fsk_detected': False, 'confidence': 0.0}
```

## 3. Multi-Modal Attack Detection

### RF-NFC Correlation System
**File**: `backend/pico/main.py` (Lines 180-210)

```python
async def handle_rf_event(event_data):
    """Handle incoming RF security events and trigger NFC correlation if needed."""
    global nfc_correlation_active, correlation_start_time, correlation_timeout
    
    try:
        threat_level = event_data.get('threat_level', 'BENIGN')
        
        # Activate NFC correlation for high-threat RF events
        if threat_level in ['HIGH', 'CRITICAL', 'MALICIOUS'] and not nfc_correlation_active:
            print(f"[CORRELATION] Activating NFC correlation for {threat_level} RF event")
            nfc_correlation_active = True
            correlation_start_time = time.time()
            
            # Send correlation activation event
            correlation_event = {
                'event_type': 'nfc_correlation_activated',
                'timestamp': time.time(),
                'trigger_event': event_data,
                'correlation_timeout': correlation_timeout
            }
            await send_event_to_server(correlation_event)
            
            # Set LED to indicate active correlation
            set_led_color('YELLOW')  # Yellow indicates active correlation mode
            
        # Handle standard RF events
        await handle_standard_rf_alert(event_data)
        
    except Exception as e:
        print(f"[ERROR] RF event handling failed: {e}")
```

## 4. Real-Time Dashboard Implementation

### Event Navigation System
**File**: `backend/cli_dashboard.py` (Lines 857-871)

```python
def handle_up(event):
    nonlocal selected_event_idx, follow_latest, first_absolute_event_requested
    if not events:
        return
    # Move selection up (earlier in time)
    selected_event_idx -= 1
    # Ensure we don't go out of bounds
    selected_event_idx = max(-len(events), min(-1, selected_event_idx))
    # Disable follow latest when manually navigating
    follow_latest = False
    # Reset the first absolute event flag when using regular navigation
    first_absolute_event_requested = False
    # Log navigation action
    if dashboard_logger:
        log_dashboard_action(dashboard_logger, "navigation", f"Up arrow - selected event index: {selected_event_idx}")
```

### Signal Visualization
**File**: `backend/cli_dashboard.py` (Lines 80-120)

```python
def generate_sparkline(values, min_value=-90, max_value=-20, width=20):
    """
    Generate a sparkline visualization using Unicode block characters.
    
    Args:
        values (list): List of numerical values to visualize
        min_value (int): Minimum value for scaling (default: -90 dBm)
        max_value (int): Maximum value for scaling (default: -20 dBm)
        width (int): Width of the sparkline (default: 20 characters)
        
    Returns:
        str: Unicode sparkline representation
    """
    if not values:
        return "" 
    
    # Ensure we don't exceed the width
    if len(values) > width:
        values = values[-width:]
    
    # Unicode block characters for different heights (1/8, 2/8, ..., 8/8)
    blocks = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    
    # Scale values to 0-8 range for block selection
    range_size = max_value - min_value
    scaled_values = []
    
    for val in values:
        # Clamp value to min_value..max_value range
        clamped = max(min_value, min(max_value, val))
        # Scale to 0..8 range for block selection
        normalized = (clamped - min_value) / range_size
        block_idx = int(normalized * 8)
        scaled_values.append(block_idx)
    
    # Generate sparkline string
    sparkline = ''
    for idx in scaled_values:
        sparkline += blocks[idx]
    
    return sparkline
```

## 5. Hardware Management System

### Automatic Hardware Detection
**File**: `backend/hardware/rtl_sdr_interface.py` (Lines 45-75)

```python
def detect_hardware(self) -> List[Dict[str, Any]]:
    """
    Detect connected RTL-SDR devices using rtl_test command.
    
    Returns:
        List of detected device information dictionaries
    """
    try:
        # Run rtl_test to detect devices
        result = subprocess.run(
            ['rtl_test', '-t'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        devices = []
        if result.returncode == 0:
            # Parse rtl_test output for device information
            lines = result.stdout.split('\n')
            for i, line in enumerate(lines):
                if 'Found' in line and 'device' in line:
                    device_info = {
                        'index': len(devices),
                        'name': line.strip(),
                        'available': True,
                        'tuner_type': 'Unknown',
                        'frequency_range': (24e6, 1766e6)  # Default RTL-SDR range
                    }
                    
                    # Look for tuner information in subsequent lines
                    for j in range(i+1, min(i+5, len(lines))):
                        if 'Tuner:' in lines[j]:
                            device_info['tuner_type'] = lines[j].split('Tuner:')[1].strip()
                            break
                    
                    devices.append(device_info)
        
        self.logger.info(f"Detected {len(devices)} RTL-SDR device(s)")
        return devices
        
    except subprocess.TimeoutExpired:
        self.logger.error("RTL-SDR detection timed out")
        return []
    except FileNotFoundError:
        self.logger.error("rtl_test command not found - RTL-SDR tools not installed")
        return []
    except Exception as e:
        self.logger.error(f"Hardware detection failed: {e}")
        return []
```

## 6. Threat Detection Engine

### Replay Attack Detection
**File**: `backend/detection/replay_attack_detector.py` (Lines 120-150)

```python
def calculate_signal_similarity(self, signal1: Dict[str, Any], signal2: Dict[str, Any]) -> float:
    """
    Calculate similarity between two signals using multiple metrics.
    
    Args:
        signal1: First signal data
        signal2: Second signal data
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    try:
        # Frequency similarity (most important for replay attacks)
        freq_diff = abs(signal1.get('frequency', 0) - signal2.get('frequency', 0))
        freq_similarity = max(0, 1 - (freq_diff / 1000000))  # 1MHz tolerance
        
        # Power level similarity
        power1 = signal1.get('power_db', -100)
        power2 = signal2.get('power_db', -100)
        power_diff = abs(power1 - power2)
        power_similarity = max(0, 1 - (power_diff / 20))  # 20dB tolerance
        
        # Timing pattern similarity (if available)
        timing_similarity = 1.0  # Default if no timing data
        if 'burst_pattern' in signal1 and 'burst_pattern' in signal2:
            pattern1 = signal1['burst_pattern']
            pattern2 = signal2['burst_pattern']
            if pattern1 and pattern2:
                timing_similarity = self._compare_burst_patterns(pattern1, pattern2)
        
        # Weighted combination of similarities
        overall_similarity = (
            freq_similarity * 0.5 +      # Frequency is most important
            power_similarity * 0.3 +     # Power level secondary
            timing_similarity * 0.2      # Timing pattern tertiary
        )
        
        return min(1.0, max(0.0, overall_similarity))
        
    except Exception as e:
        self.logger.error(f"Signal similarity calculation failed: {e}")
        return 0.0
```

## 7. Testing Framework

### Detection Accuracy Validation
**File**: `backend/utils/validate_detection_accuracy.py` (Lines 80-120)

```python
async def run_accuracy_validation(num_samples: int = 100, output_dir: str = None) -> Dict[str, Any]:
    """
    Run comprehensive detection accuracy validation.
    
    Args:
        num_samples: Number of test samples to generate
        output_dir: Directory to save results
        
    Returns:
        Validation results dictionary
    """
    print(f"🔍 Running detection accuracy validation with {num_samples} samples...")
    
    # Initialize components
    analyzer = AutomotiveSignalAnalyzer()
    detector = SecurityAnalyzer()
    
    # Generate test dataset
    test_data = []
    ground_truth = []
    
    for i in range(num_samples):
        # Generate different types of signals
        signal_type = random.choice(['key_fob', 'tpms', 'jamming', 'replay', 'benign'])
        
        if signal_type == 'key_fob':
            signal = generate_key_fob_signal()
            expected = 'SUSPICIOUS'
        elif signal_type == 'tpms':
            signal = generate_tpms_signal()
            expected = 'BENIGN'
        elif signal_type == 'jamming':
            signal = generate_jamming_signal()
            expected = 'MALICIOUS'
        elif signal_type == 'replay':
            signal = generate_replay_signal()
            expected = 'MALICIOUS'
        else:  # benign
            signal = generate_benign_signal()
            expected = 'BENIGN'
        
        test_data.append(signal)
        ground_truth.append(expected)
    
    # Run detection on test data
    predictions = []
    processing_times = []
    
    for signal in test_data:
        start_time = time.time()
        
        # Analyze signal
        features = analyzer.analyze_signal(signal['samples'], signal['sample_rate'])
        events = await detector.analyze_signal_features(features)
        
        # Get highest threat level
        if events:
            threat_level = max([event.get('threat_level', 'BENIGN') for event in events])
        else:
            threat_level = 'BENIGN'
        
        predictions.append(threat_level)
        processing_times.append(time.time() - start_time)
    
    # Calculate accuracy metrics
    accuracy = accuracy_score(ground_truth, predictions)
    precision = precision_score(ground_truth, predictions, average='weighted', zero_division=0)
    recall = recall_score(ground_truth, predictions, average='weighted', zero_division=0)
    f1 = f1_score(ground_truth, predictions, average='weighted', zero_division=0)
    
    # Performance metrics
    avg_processing_time = np.mean(processing_times)
    max_processing_time = np.max(processing_times)
    
    results = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'avg_processing_time_ms': avg_processing_time * 1000,
        'max_processing_time_ms': max_processing_time * 1000,
        'total_samples': num_samples,
        'meets_accuracy_requirement': accuracy >= 0.9,  # 90% requirement
        'meets_performance_requirement': avg_processing_time < 0.1  # 100ms requirement
    }
    
    print(f"✅ Validation complete:")
    print(f"   Accuracy: {accuracy:.2%} (Requirement: ≥90%)")
    print(f"   Precision: {precision:.2%}")
    print(f"   Recall: {recall:.2%}")
    print(f"   F1-Score: {f1:.2%}")
    print(f"   Avg Processing Time: {avg_processing_time*1000:.1f}ms (Requirement: <100ms)")
    
    return results
```

## File References Summary

For screenshot purposes, here are the key files and line numbers:

1. **Signal Threshold**: `backend/rtl_sdr/signal_bridge.py` - Line 88
2. **FSK Detection**: `backend/rtl_sdr/automotive_signal_analyzer.py` - Lines 89-110
3. **NFC Correlation**: `backend/pico/main.py` - Lines 180-210
4. **Dashboard Navigation**: `backend/cli_dashboard.py` - Lines 857-871
5. **Signal Visualization**: `backend/cli_dashboard.py` - Lines 80-120
6. **Hardware Detection**: `backend/hardware/rtl_sdr_interface.py` - Lines 45-75
7. **Replay Detection**: `backend/detection/replay_attack_detector.py` - Lines 120-150
8. **Accuracy Validation**: `backend/utils/validate_detection_accuracy.py` - Lines 80-120

These code snippets demonstrate the key technical implementations of the automotive security monitoring system, including signal processing, threat detection, hardware management, and validation frameworks.