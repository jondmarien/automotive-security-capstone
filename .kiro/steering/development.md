# Development Workflow & Best Practices

## Development Environment Setup

### Prerequisites and System Requirements

#### Hardware Requirements

- **Development Machine**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: Minimum 8GB, recommended 16GB for signal processing
- **Storage**: 10GB free space for development environment and recordings
- **USB Ports**: USB 3.0 port for RTL-SDR V4 dongle
- **Network**: WiFi or Ethernet for Pico W development

#### Software Prerequisites

```bash
# Python Environment
Python 3.11+ (required for modern type hints and performance)
uv or pip (package management)
git (version control)

# RTL-SDR Tools (Windows)
RTL-SDR drivers and utilities (included in rtl_sdr_bin/)
Zadig driver installer (for USB driver management)

# Development Tools
VS Code or equivalent (with Pico W MicroPython plugin)
Windows Terminal or equivalent (for CLI dashboard)
```

### Environment Setup Workflow

#### 1. Repository Setup

```bash
# Clone repository
git clone <repository-url>
cd automotive-security-capstone

# Navigate to backend
cd backend

# Create virtual environment (UV preferred)
uv venv
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt

# Alternative with pip
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### 2. Hardware Setup

```bash
# Test RTL-SDR connection
rtl_test

# If driver issues on Windows:
# 1. Run Zadig as administrator
# 2. Select RTL-SDR device
# 3. Install WinUSB driver

# Test RTL-TCP server
rtl_tcp -a 127.0.0.1 -p 1234
# Should show "listening on 127.0.0.1:1234"
```

#### 3. Development Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# RTL_SDR_DEVICE=0
# LOG_LEVEL=DEBUG
# MOCK_MODE=false

# Run initial tests
pytest tests/test_basic_functionality.py
```

## Git Workflow and Version Control

### Branch Strategy (Git Flow)

#### Main Branches

- **main**: Production-ready code, stable releases
- **develop**: Integration branch for features, latest development
- **feature/***: Individual feature development branches
- **hotfix/***: Critical bug fixes for production
- **release/***: Release preparation and stabilization

#### Branch Naming Conventions

```bash
# Feature branches
feature/rtl-sdr-integration
feature/threat-detection-algorithm
feature/pico-w-alerts

# Bug fix branches
bugfix/memory-leak-signal-processing
bugfix/tcp-connection-timeout

# Hotfix branches
hotfix/critical-security-vulnerability
hotfix/system-crash-on-startup

# Release branches
release/v1.0.0
release/v1.1.0-beta
```

#### Commit Message Standards

```bash
# Format: <type>(<scope>): <description>
# Types: feat, fix, docs, style, refactor, test, chore

# Examples
feat(detection): add TPMS spoofing detection algorithm
fix(rtl-sdr): resolve memory leak in signal processing
docs(api): update threat detection API documentation
test(integration): add end-to-end system tests
refactor(hardware): improve RTL-SDR abstraction layer
style(cli): format dashboard code with black
chore(deps): update numpy to latest version
```

### Code Review Process

#### Pull Request Requirements

- **Automated Tests**: All tests must pass
- **Code Coverage**: Maintain >90% coverage for new code
- **Documentation**: Update relevant documentation
- **Security Review**: Security-sensitive changes require security review
- **Performance**: No significant performance regressions

#### Review Checklist

```markdown
## Code Review Checklist

### Functionality
- [ ] Code implements requirements correctly
- [ ] Edge cases are handled appropriately
- [ ] Error handling is comprehensive
- [ ] Performance is acceptable

### Code Quality
- [ ] Code follows project style guidelines
- [ ] Functions and classes have clear responsibilities
- [ ] Code is well-documented with docstrings
- [ ] Type hints are comprehensive and accurate

### Security
- [ ] Input validation is implemented
- [ ] No sensitive data in logs or outputs
- [ ] Secure coding practices followed
- [ ] Dependencies are up-to-date and secure

### Testing
- [ ] Unit tests cover new functionality
- [ ] Integration tests verify system behavior
- [ ] Tests are maintainable and reliable
- [ ] Mock objects used appropriately
```

## Testing Strategy and Quality Assurance

### Test Categories and Organization

#### Unit Tests (Fast, Isolated)

```python
# tests/test_detection/test_threat_levels.py
@pytest.mark.unit
def test_threat_level_classification():
    """Test threat level enum and classification logic."""
    assert ThreatLevel.BENIGN.value < ThreatLevel.SUSPICIOUS.value
    assert ThreatLevel.SUSPICIOUS.value < ThreatLevel.MALICIOUS.value

@pytest.mark.unit
def test_packet_parsing():
    """Test RF packet parsing and validation."""
    packet_data = b'\x01\x02\x03\x04'
    packet = Packet(payload=packet_data, freq=433.92e6, rssi=-50.0)
    assert packet.freq == 433.92e6
    assert packet.rssi == -50.0
```

#### Integration Tests (Component Interaction)

```python
# tests/integration/test_detection_pipeline.py
@pytest.mark.integration
async def test_detection_pipeline():
    """Test complete detection pipeline from signal to alert."""
    # Setup mock RTL-SDR
    mock_rtl = MockRTLSDR()
    
    # Inject test signal
    test_signal = generate_key_fob_signal(freq=433.92e6)
    mock_rtl.inject_signal(test_signal)
    
    # Run detection pipeline
    detector = SecurityAnalyzer()
    events = await detector.analyze_signal(test_signal)
    
    # Verify detection
    assert len(events) > 0
    assert events[0].threat_level == ThreatLevel.SUSPICIOUS
```

#### Hardware Tests (Require Physical Hardware)

```python
# tests/test_hardware/test_rtl_sdr_integration.py
@pytest.mark.hardware
def test_rtl_sdr_connection():
    """Test actual RTL-SDR hardware connection."""
    rtl_sdr = RTLSDRInterface()
    assert rtl_sdr.is_connected()
    
    # Test signal capture
    samples = rtl_sdr.capture_samples(duration=1.0)
    assert len(samples) > 0
    assert isinstance(samples[0], complex)
```

#### Performance Tests (Resource Usage)

```python
# tests/test_performance/test_real_time_processing.py
@pytest.mark.slow
def test_real_time_processing_performance():
    """Test system can handle real-time signal processing."""
    processor = SignalProcessor()
    
    # Generate continuous signal stream
    signal_generator = ContinuousSignalGenerator(duration=60.0)
    
    start_time = time.time()
    processed_samples = 0
    
    for signal_chunk in signal_generator:
        processor.process_chunk(signal_chunk)
        processed_samples += len(signal_chunk)
    
    end_time = time.time()
    processing_rate = processed_samples / (end_time - start_time)
    
    # Must process at least 2 MS/s for real-time operation
    assert processing_rate >= 2e6
```

#### Test Quality Improvements (Recent Updates)

The testing framework has been enhanced with improved data realism and temporal accuracy:

- **Realistic Timestamps**: Tests now use proper Unix timestamps with chronological ordering to accurately simulate real-world signal processing scenarios
- **Temporal Analysis Testing**: Jamming detector tests include proper time-based signal history for accurate noise floor baseline calculation
- **Enhanced Coverage**: Detection tests now cover >90% of code paths with realistic signal data
- **Performance Validation**: Tests verify real-time processing requirements (<500ms for 100ms signal chunks) with optimized timing analysis

```python
# Example of improved test data with realistic timestamps
def test_noise_floor_analysis_with_timestamps():
    """Test noise floor analysis with proper temporal ordering."""
    signal_history = []
    for i in range(10):
        signal = create_test_signal()
        signal['timestamp'] = time.time() - (10 - i) * 0.1  # Chronological order
        signal_history.append(signal)
    
    # Current signal with proper timestamp
    current_signal = create_test_signal()
    current_signal['timestamp'] = time.time()
    
    # Test temporal analysis
    result = detector.analyze_with_history(current_signal, signal_history)
    assert result['temporal_accuracy'] > 0.95
```

### Test Execution and Automation

#### Local Testing Workflow

```bash
# Run all tests
pytest

# Run enhanced signal processing tests (NEW)
pytest tests/test_automotive_signal_analyzer.py -v    # Signal analyzer tests (24 tests)
pytest tests/test_enhanced_signal_bridge.py -v       # Enhanced bridge tests (21 tests)
pytest tests/test_jamming_detector.py -v             # Jamming detection tests (18 tests)
pytest tests/test_automotive_signal_analyzer.py tests/test_enhanced_signal_bridge.py tests/test_jamming_detector.py -v  # All enhanced tests (63 total)

# Run specific test categories
pytest -m unit                    # Fast unit tests only
pytest -m "not hardware"         # Skip hardware-dependent tests
pytest -m integration            # Integration tests only
pytest -m slow                   # Long-running tests

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test files
pytest tests/test_detection/
pytest tests/test_rtl_sdr/test_signal_bridge.py
pytest tests/test_cli_dashboard.py  # CLI dashboard tests with event navigation and technical evidence

# Run with verbose output
pytest -v -s                     # Show test names and print statements

# Performance testing for enhanced components (optimized for real-time processing)
pytest tests/test_automotive_signal_analyzer.py::TestAutomotiveSignalAnalyzer::test_performance -v
```

#### Continuous Integration Pipeline

```yaml
# .github/workflows/ci.yml
name: Continuous Integration

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install uv
        uv pip install -r requirements.txt
        uv pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        black --check .
        isort --check-only .
        flake8
        mypy .
    
    - name: Run tests
      run: |
        pytest -m "not hardware" --cov=backend --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Code Quality Standards

#### Automated Code Formatting

```bash
# Format code automatically
black .                          # Code formatting
isort .                         # Import sorting

# Check formatting without changes
black --check .
isort --check-only .
```

#### Linting and Static Analysis

```bash
# Style and complexity checking
flake8                          # PEP 8 compliance and complexity

# Type checking
mypy .                          # Static type analysis

# Security scanning
bandit -r backend/              # Security vulnerability scanning
safety check                   # Dependency vulnerability checking
```

#### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
```

## Development Workflow Patterns

### Feature Development Lifecycle

#### 1. Planning and Design

```bash
# Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/new-detection-algorithm

# Document feature requirements
# Update docs/plans/feature_requirements.md
# Create or update architecture diagrams
```

#### 2. Test-Driven Development (TDD)

```python
# 1. Write failing test first
def test_new_detection_algorithm():
    detector = NewDetectionAlgorithm()
    result = detector.detect_threat(sample_signal)
    assert result.threat_level == ThreatLevel.MALICIOUS

# 2. Implement minimal code to pass test
class NewDetectionAlgorithm:
    def detect_threat(self, signal):
        # Minimal implementation
        return ThreatEvent(threat_level=ThreatLevel.MALICIOUS)

# 3. Refactor and improve implementation
class NewDetectionAlgorithm:
    def detect_threat(self, signal):
        # Full implementation with proper logic
        analysis_result = self._analyze_signal_patterns(signal)
        return self._classify_threat(analysis_result)
```

#### 3. Integration and Testing

```bash
# Run comprehensive tests
pytest                          # All tests (now includes 45 enhanced signal processing tests)
pytest --cov                   # With coverage

# Test enhanced signal processing components
pytest tests/test_automotive_signal_analyzer.py tests/test_enhanced_signal_bridge.py --cov=rtl_sdr --cov-report=html

# Test with hardware (if available)
pytest -m hardware

# Performance testing (optimized for real-time signal processing)
pytest -m slow
pytest tests/test_automotive_signal_analyzer.py::TestAutomotiveSignalAnalyzer::test_performance -v
```

#### 4. Code Review and Merge

```bash
# Push feature branch
git push origin feature/new-detection-algorithm

# Create pull request
# - Automated tests run
# - Code review by team members
# - Security review if needed

# Merge to develop after approval
git checkout develop
git merge feature/new-detection-algorithm
git push origin develop
```

### Debugging and Troubleshooting

#### Debug Configuration

```python
# backend/config/debug.yaml
system:
  log_level: "DEBUG"
  debug_mode: true

rtl_sdr:
  mock_mode: true
  debug_signals: true
  save_raw_samples: true

detection:
  debug_classification: true
  save_intermediate_results: true
```

#### Debugging Tools and Techniques

```python
# Logging for debugging
import logging
logger = logging.getLogger(__name__)

def analyze_signal(self, signal):
    logger.debug(f"Analyzing signal: freq={signal.freq}, len={len(signal.samples)}")
    
    # Debug intermediate results
    fft_result = np.fft.fft(signal.samples)
    logger.debug(f"FFT peak frequency: {np.argmax(np.abs(fft_result))}")
    
    # Conditional debugging
    if self.debug_mode:
        self._save_debug_data(signal, fft_result)
    
    return self._classify_signal(fft_result)

# Performance profiling
import cProfile
import pstats

def profile_detection_performance():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run detection algorithm
    detector.analyze_signal(test_signal)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions by time
```

#### Common Issues and Solutions

```python
# Issue: RTL-SDR connection problems
def diagnose_rtl_sdr_issues():
    """Diagnose and resolve common RTL-SDR issues."""
    try:
        # Test basic connection
        rtl_test_result = subprocess.run(['rtl_test'], capture_output=True)
        if rtl_test_result.returncode != 0:
            logger.error("RTL-SDR hardware not detected")
            return False
        
        # Test driver installation
        if "No supported devices found" in rtl_test_result.stdout.decode():
            logger.error("RTL-SDR driver not installed correctly")
            return False
        
        return True
    except FileNotFoundError:
        logger.error("RTL-SDR tools not installed")
        return False

# Issue: Memory leaks in signal processing
def monitor_memory_usage():
    """Monitor memory usage during signal processing."""
    import psutil
    import gc
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    # Process signals
    for i in range(1000):
        signal = generate_test_signal()
        result = process_signal(signal)
        
        # Force garbage collection periodically
        if i % 100 == 0:
            gc.collect()
            current_memory = process.memory_info().rss
            memory_growth = current_memory - initial_memory
            logger.info(f"Memory usage after {i} signals: {memory_growth / 1024 / 1024:.2f} MB")
```

### Performance Optimization Guidelines

#### Signal Processing Optimization

```python
# Use NumPy vectorized operations
def efficient_fft_analysis(signal_samples):
    """Efficient FFT analysis using NumPy vectorization."""
    # Good: Vectorized operation
    fft_result = np.fft.fft(signal_samples)
    magnitude = np.abs(fft_result)
    peak_freq = np.argmax(magnitude)
    
    # Avoid: Loop-based processing
    # magnitude = [abs(sample) for sample in fft_result]  # Slow!
    
    return peak_freq, magnitude

# Memory-efficient signal processing
def process_signal_chunks(signal_stream, chunk_size=1024):
    """Process signal in chunks to manage memory usage."""
    for chunk in signal_stream.read_chunks(chunk_size):
        # Process chunk immediately
        result = analyze_chunk(chunk)
        yield result
        
        # Don't accumulate chunks in memory
        del chunk
```

#### Real-time Performance Requirements

```python
# Performance monitoring
class PerformanceMonitor:
    def __init__(self):
        self.processing_times = []
        self.max_processing_time = 0.1  # 100ms max for real-time
    
    def measure_processing_time(self, func):
        """Decorator to measure function execution time."""
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            
            processing_time = end_time - start_time
            self.processing_times.append(processing_time)
            
            if processing_time > self.max_processing_time:
                logger.warning(f"Processing time exceeded limit: {processing_time:.3f}s")
            
            return result
        return wrapper
```

This comprehensive development workflow ensures high-quality, maintainable code while supporting the educational and research goals of the automotive security capstone project.
