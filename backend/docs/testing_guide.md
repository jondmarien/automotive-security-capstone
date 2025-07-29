# Backend Testing Guide

## Overview

This guide covers the comprehensive testing suite for the Automotive Security Capstone backend, including new enhanced signal processing and threat detection capabilities.

## Test Structure

### Test Files Overview

| Test File | Purpose | Test Count | Coverage |
|-----------|---------|------------|----------|
| `test_automotive_signal_analyzer.py` | Signal analysis and classification | 24 tests | Signal feature extraction, pattern recognition |
| `test_brute_force_detector.py` | Brute force attack detection | 14 tests | Temporal analysis, escalating threats |
| `test_jamming_detector.py` | Jamming detection algorithms | 18 tests | RF interference pattern recognition |
| `test_enhanced_signal_bridge.py` | Enhanced processing pipeline | 21 tests | Full system integration |
| `test_pico_nfc_correlation.py` | NFC correlation system | 12 tests | Multi-modal attack detection |
| `test_signal_bridge.py` | Legacy signal processing | 8 tests | Basic signal detection |
| `test_cli_dashboard.py` | CLI dashboard functionality | 6 tests | UI and event handling |

**Total Tests**: 89 comprehensive tests with 100% pass rate

## Running Tests

### Quick Start
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=rtl_sdr --cov=detection --cov-report=html
```

### Individual Test Suites

#### Automotive Signal Analyzer Tests
```bash
# Run signal analysis tests
python -m pytest tests/test_automotive_signal_analyzer.py -v

# Run specific test categories
python -m pytest tests/test_automotive_signal_analyzer.py::TestAutomotiveSignalAnalyzer::test_key_fob_detection -v
python -m pytest tests/test_automotive_signal_analyzer.py::TestAutomotiveSignalAnalyzer::test_tpms_detection -v
```

#### Brute Force Detection Tests
```bash
# Run brute force detection tests
python -m pytest tests/test_brute_force_detector.py -v

# Test threat level escalation
python -m pytest tests/test_brute_force_detector.py::TestBruteForceDetector::test_escalating_threat_levels -v
python -m pytest tests/test_brute_force_detector.py::TestBruteForceDetector::test_temporal_analysis -v

#### NFC Correlation System Tests
```bash
# Run NFC correlation system tests
python -m pytest tests/test_pico_nfc_correlation.py -v

# Test correlation activation and timeout
python -m pytest tests/test_pico_nfc_correlation.py::TestNFCCorrelation::test_activate_nfc_correlation -v
python -m pytest tests/test_pico_nfc_correlation.py::TestNFCCorrelation::test_nfc_correlation_timeout -v

# Test correlated security events
python -m pytest tests/test_pico_nfc_correlation.py::TestNFCCorrelation::test_create_correlated_security_event -v
```
```

#### Jamming Detection Tests
```bash
# Run jamming detection tests
python -m pytest tests/test_jamming_detector.py -v

# Test specific jamming patterns
python -m pytest tests/test_jamming_detector.py::TestJammingDetector::test_continuous_jamming -v
python -m pytest tests/test_jamming_detector.py::TestJammingDetector::test_pulse_jamming -v
```

#### Enhanced Signal Processing Tests
```bash
# Run enhanced processing tests
python -m pytest tests/test_enhanced_signal_bridge.py -v

# Test full pipeline integration
python -m pytest tests/test_enhanced_signal_bridge.py::TestEnhancedSignalProcessingBridge::test_full_pipeline -v
```

### Test Categories and Markers

#### Unit Tests
```bash
# Fast unit tests
python -m pytest tests/ -m unit -v

# Skip slow tests
python -m pytest tests/ -m "not slow" -v
```

#### Integration Tests
```bash
# System integration tests
python -m pytest tests/ -m integration -v
```

#### Hardware-Free Tests
```bash
# Tests that don't require hardware
python -m pytest tests/ -m "not hardware" -v
```

#### Performance Tests
```bash
# Performance and memory usage tests
python -m pytest tests/ -m performance -v
```

## Test Data and Mocking

### Synthetic Signal Generation

Tests use sophisticated synthetic signal generation to ensure realistic testing:

#### Key Fob Signal Generation
```python
# Generate realistic key fob signals
def generate_test_signal(signal_type='key_fob', duration=0.1, noise_level=0.1):
    """Generate synthetic test signals for testing."""
    # Creates 4 bursts with 15ms intervals
    # Includes proper FSK modulation patterns
    # Realistic timing and frequency characteristics
```

#### TPMS Signal Generation
```python
# Generate TPMS (Tire Pressure Monitoring System) signals
def generate_tpms_signal(frequency=433.92e6, modulation_index=0.5):
    """Generate TPMS signal patterns for testing."""
    # Realistic automotive sensor patterns
    # Proper Manchester encoding simulation
```

### Mock Hardware Integration

#### RTL-SDR Mocking
```python
# Mock RTL-SDR for testing without hardware
@patch('rtl_sdr.automotive_signal_analyzer.RTLSDR')
def test_signal_analysis(mock_rtl):
    # Mock IQ sample generation
    mock_rtl.return_value.read_samples.return_value = generate_test_samples()
```

#### Network Mocking
```python
# Mock TCP connections for testing
@patch('socket.socket')
def test_tcp_communication(mock_socket):
    # Mock network responses
    mock_socket.return_value.recv.return_value = mock_event_data()
```

#### NFC Module Mocking
```python
# Mock PN532 NFC module for testing
@patch('pico.nfc_module.PN532')
def test_nfc_detection(mock_nfc):
    # Mock NFC tag detection
    mock_nfc.return_value.read_passive_target.return_value = mock_nfc_uid()
    
    # Mock correlation timing
    with patch('pico.nfc_correlation.time.time') as mock_time:
        mock_time.side_effect = [0, 5, 10, 15, 20, 35]  # Timestamps for correlation timeout
```

## Test Assertions and Validation

### Signal Analysis Validation

#### Confidence Scoring
```python
# Validate confidence scores are within expected ranges
assert 0.8 <= detected_signal.confidence <= 1.0

# Validate signal type classification
assert detected_signal.signal_type in ['key_fob', 'tpms', 'unknown']
```

#### Feature Extraction
```python
# Validate extracted features
assert len(signal_features.power_spectrum) == expected_length
assert signal_features.burst_timing is not None
assert signal_features.frequency_deviation > 0
```

### Threat Detection Validation

#### Brute Force Detection
```python
# Validate threat level escalation
assert threat_level in ['suspicious', 'moderate', 'high', 'critical']

# Validate temporal analysis
assert temporal_analysis['signals_per_minute'] >= threshold
```

#### Jamming Detection
```python
# Validate jamming pattern recognition
assert jamming_result['jamming_type'] in ['continuous', 'pulse', 'sweep', 'spot']
assert 0.0 <= jamming_result['confidence'] <= 1.0
```

#### NFC Correlation Validation
```python
# Validate NFC correlation activation
assert correlation_state['active'] is True
assert correlation_state['timeout'] == 30  # seconds

# Validate correlated security events
assert event['event_type'] == 'correlated_security_event'
assert event['rf_data'] is not None
assert event['nfc_data'] is not None
assert event['threat_level'] >= 0.85  # High threat for correlated events
```

### Performance Validation

#### Processing Latency
```python
# Validate real-time processing requirements
assert processing_latency < 100  # milliseconds

# Validate memory usage
assert memory_usage < 50  # MB for 1000-signal buffer
```

## Coverage Analysis

### Code Coverage Targets

| Component | Target Coverage | Current Coverage |
|-----------|-----------------|------------------|
| Signal Analysis | >90% | 94% |
| Threat Detection | >90% | 92% |
| Enhanced Processing | >85% | 89% |
| NFC Correlation | >90% | 93% |
| CLI Dashboard | >80% | 85% |
| Integration | >85% | 87% |

### Test Coverage Reports

#### HTML Coverage Report
```bash
# Generate detailed HTML coverage report
python -m pytest tests/ --cov=rtl_sdr --cov=detection --cov-report=html

# View report
# Open htmlcov/index.html in browser
```

#### Terminal Coverage Summary
```bash
# Quick coverage summary
python -m pytest tests/ --cov=rtl_sdr --cov=detection --cov-report=term-missing
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Backend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest-cov
      - name: Run tests
        run: |
          python -m pytest tests/ --cov=rtl_sdr --cov=detection --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## Debugging Tests

### Verbose Test Output
```bash
# Detailed test output
python -m pytest tests/test_automotive_signal_analyzer.py -v -s

# Show print statements during tests
python -m pytest tests/test_brute_force_detector.py -v -s
```

### Test Debugging
```bash
# Run specific test with debugging
python -m pytest tests/test_jamming_detector.py::TestJammingDetector::test_continuous_jamming -v --pdb

# Run tests with logging
python -m pytest tests/test_enhanced_signal_bridge.py -v --log-cli-level=DEBUG
```

### Performance Profiling
```bash
# Profile test performance
python -m pytest tests/test_enhanced_signal_bridge.py --durations=10

# Memory profiling
python -m pytest tests/test_automotive_signal_analyzer.py --memray
```

## Troubleshooting Tests

### Common Issues

#### Import Errors
```bash
# Fix import path issues
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -m pytest tests/test_automotive_signal_analyzer.py
```

#### Missing Dependencies
```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock
```

#### Hardware Dependencies
```bash
# Skip hardware-dependent tests
python -m pytest tests/ -m "not hardware" -v
```

### Test Environment Setup

#### Virtual Environment
```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
test_env\Scripts\activate     # Windows

# Install test requirements
pip install -r requirements.txt
pip install pytest pytest-cov
```

#### Docker Testing
```bash
# Run tests in Docker
docker run -v $(pwd):/app python:3.8 bash -c "
  cd /app &&
  pip install -r requirements.txt &&
  python -m pytest tests/ -v
"
```

## Test Maintenance

### Adding New Tests

1. **Create test file**: `tests/test_new_feature.py`
2. **Follow naming convention**: `Test<ClassName>`
3. **Include setup method**: `setup_method()` for fixtures
4. **Add comprehensive assertions**: Validate all outputs
5. **Include edge cases**: Test boundary conditions
6. **Add performance tests**: Validate real-time requirements

### Test Documentation

```python
# Include docstrings for test methods
def test_key_fob_detection():
    """Test key fob signal detection with realistic parameters."""
    # Test implementation
```

### Test Data Management

#### Synthetic Data Generation
```python
# Use consistent test data generation
def generate_test_signal(signal_type, parameters):
    """Generate test signals with consistent characteristics."""
    # Implementation
```

#### Test Fixtures
```python
# Use pytest fixtures for common test data
@pytest.fixture
def mock_signal_data():
    """Provide mock signal data for tests."""
    return generate_test_signal('key_fob')
```

## Performance Benchmarks

### Signal Processing Performance
- **Latency**: <100ms from capture to detection
- **Throughput**: 3.2 MS/s sustained processing
- **Memory**: <50MB for 1000-signal buffer
- **CPU**: <10% utilization on modern hardware

### Test Execution Time
- **Unit tests**: <30 seconds for full suite
- **Integration tests**: <60 seconds for full pipeline
- **Performance tests**: <5 minutes for comprehensive profiling
