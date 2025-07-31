# Validation Framework API Documentation

## Overview

The Validation Framework provides comprehensive testing and validation capabilities for the automotive security detection system. It includes synthetic event generation, accuracy validation, confusion matrix analysis, and demonstration scenarios to ensure the system meets the >90% detection accuracy requirement.

## Core Components

### DetectionAccuracyValidator

Validates detection system accuracy using synthetic events with known ground truth labels.

```python
from utils.detection_accuracy import DetectionAccuracyValidator
import asyncio

# Initialize validator
validator = DetectionAccuracyValidator()

# Run accuracy evaluation
results = await validator.evaluate_detection_accuracy(num_samples=100)

# Print results
accuracy = results["accuracy_metrics"]["overall_accuracy"]
print(f"Overall Accuracy: {accuracy:.2%}")

# Generate confusion matrix
validator.generate_confusion_matrix(save_path="confusion_matrix.png")

# Save detailed results
validator.save_results_to_file(results, "accuracy_results.md")
```

### Demo Scenarios

Structured demonstration scenarios for capstone presentations and testing.

```python
from demo_scenarios import (
    NormalOperationScenario,
    ReplayAttackScenario,
    JammingAttackScenario,
    BruteForceAttackScenario,
    ComprehensiveDemoScenario
)

# Run comprehensive demo
scenario = ComprehensiveDemoScenario()
events = await scenario.run()
print(f"Generated {len(events)} demonstration events")

# Run specific attack scenario
replay_scenario = ReplayAttackScenario()
replay_events = await replay_scenario.run()
```

### Signal Constants

Centralized constants for automotive RF signal parameters and configurations.

```python
from utils.signal_constants import (
    KEY_FOB_FREQUENCIES,
    MANUFACTURER_PARAMETERS,
    ModulationType,
    AttackType,
    NFCTagType
)

# Access frequency definitions
eu_frequency = KEY_FOB_FREQUENCIES["EU_STANDARD"]  # 433.92 MHz
us_frequency = KEY_FOB_FREQUENCIES["US_STANDARD"]  # 315.0 MHz

# Get manufacturer-specific parameters
toyota_params = MANUFACTURER_PARAMETERS["Toyota"]
print(f"Toyota frequency: {toyota_params['frequency']/1e6:.2f} MHz")
print(f"Modulation: {toyota_params['modulation']}")
print(f"Rolling code bits: {toyota_params['rolling_code_bits']}")
```

## Validation Methods

### Accuracy Validation

```python
# Run comprehensive accuracy validation
async def validate_system_accuracy():
    validator = DetectionAccuracyValidator()
    
    # Generate test dataset
    test_data = await validator.generate_test_dataset(num_samples=200)
    
    # Evaluate accuracy
    results = await validator.evaluate_detection_accuracy(num_samples=200)
    
    # Check requirements
    accuracy = results["accuracy_metrics"]["overall_accuracy"]
    real_time_met = results["performance_metrics"]["real_time_requirement_met"]
    
    print(f"Accuracy: {accuracy:.2%} ({'PASS' if accuracy >= 0.9 else 'FAIL'})")
    print(f"Real-time: {'PASS' if real_time_met else 'FAIL'}")
    
    return results
```

### Performance Metrics

```python
# Performance metrics included in validation results
performance_metrics = {
    "avg_processing_time_ms": 45.2,
    "min_processing_time_ms": 12.1,
    "max_processing_time_ms": 89.7,
    "processing_time_p95_ms": 78.3,
    "processing_time_p99_ms": 85.9,
    "real_time_requirement_met": True  # <500ms requirement
}
```

### Accuracy Metrics

```python
# Accuracy metrics with per-class breakdown
accuracy_metrics = {
    "overall_accuracy": 0.94,  # 94% overall accuracy
    "average_confidence": 0.87,
    "class_metrics": {
        "benign": {
            "precision": 0.96,
            "recall": 0.98,
            "f1_score": 0.97,
            "support": 50
        },
        "replay_attack": {
            "precision": 0.89,
            "recall": 0.85,
            "f1_score": 0.87,
            "support": 10
        },
        # ... other attack types
    }
}
```

## Demonstration Scenarios

### Scenario Types

```python
from demo_scenarios import DemonstrationScenario

class CustomScenario(DemonstrationScenario):
    def __init__(self):
        super().__init__(
            "Custom Attack",
            "Demonstrates custom attack pattern"
        )
    
    async def run(self):
        # Generate custom events
        for i in range(5):
            event = self.generate_custom_event(i)
            self.events.append(event)
            await asyncio.sleep(1.0)
        
        return self.events
```

### Built-in Scenarios

#### Normal Operation
```python
# Demonstrates normal key fob operation
scenario = NormalOperationScenario()
events = await scenario.run()
# Generates: lock/unlock sequences with realistic timing
```

#### Replay Attack
```python
# Demonstrates replay attack sequence
scenario = ReplayAttackScenario()
events = await scenario.run()
# Generates: legitimate signal followed by replay attempts
```

#### Jamming Attack
```python
# Demonstrates jamming attack
scenario = JammingAttackScenario()
events = await scenario.run()
# Generates: progressive jamming interference patterns
```

#### Brute Force Attack
```python
# Demonstrates brute force attack
scenario = BruteForceAttackScenario()
events = await scenario.run()
# Generates: rapid code attempt sequences
```

#### Comprehensive Demo
```python
# Runs all scenarios in sequence
scenario = ComprehensiveDemoScenario()
events = await scenario.run()
# Generates: complete demonstration with all attack types
```

## Synthetic Event Generation

### Event Generation Functions

```python
from cli_dashboard_detection_adapter import (
    generate_synthetic_key_fob_event,
    generate_synthetic_replay_attack,
    generate_synthetic_jamming_attack,
    generate_synthetic_brute_force_attack
)

# Generate benign key fob event
benign_event = generate_synthetic_key_fob_event("benign")

# Generate replay attack based on original event
original_event = generate_synthetic_key_fob_event("benign")
replay_event = generate_synthetic_replay_attack(original_event)

# Generate jamming attack at specific step
jamming_event = generate_synthetic_jamming_attack(step=2)

# Generate brute force attack sequence
brute_force_event = generate_synthetic_brute_force_attack(step=3)
```

### Event Structure

```python
# Standard event structure
synthetic_event = {
    "timestamp": "2025-07-31 12:34:56",
    "type": "RF Replay Attack",
    "threat": "MALICIOUS",
    "source": "RTL-SDR",
    "frequency": 433920000,
    "rssi": -45.2,
    "snr": 12.8,
    "modulation": "FSK",
    "burst_count": 3,
    "confidence": 0.89,
    "details": "Detected replay of previously captured signal",
    "technical_evidence": {
        "signal_similarity": 0.94,
        "temporal_clustering": "High",
        "pattern_match": "Exact duplicate detected"
    }
}
```

## Signal Constants and Parameters

### Frequency Definitions

```python
KEY_FOB_FREQUENCIES = {
    "EU_STANDARD": 433.92e6,    # European standard
    "US_STANDARD": 315.0e6,     # US standard
    "EU_ALTERNATIVE": 868.0e6,  # Alternative European
    "US_ALTERNATIVE": 915.0e6,  # Alternative US
    "BLUETOOTH": 2.4e9          # Bluetooth frequency
}
```

### Manufacturer Parameters

```python
MANUFACTURER_PARAMETERS = {
    "Toyota": {
        "frequency": 433.92e6,
        "modulation": "FSK",
        "rolling_code_bits": 24
    },
    "Honda": {
        "frequency": 433.92e6,
        "modulation": "GFSK",
        "rolling_code_bits": 32
    },
    "Ford": {
        "frequency": 315.0e6,
        "modulation": "ASK",
        "rolling_code_bits": 40
    },
    # ... additional manufacturers
}
```

### Enumeration Types

```python
class ModulationType(Enum):
    FSK = "FSK"           # Frequency Shift Keying
    GFSK = "GFSK"         # Gaussian FSK
    ASK = "ASK"           # Amplitude Shift Keying
    OOK = "OOK"           # On-Off Keying
    PSK = "PSK"           # Phase Shift Keying
    NOISE = "Noise"       # Noise/Interference
    WIDEBAND = "Wideband" # Wideband interference

class AttackType(Enum):
    REPLAY = "replay"
    JAMMING = "jamming"
    BRUTE_FORCE = "brute_force"
    SIGNAL_CLONING = "signal_cloning"
    RELAY = "relay"

class NFCTagType(Enum):
    ISO14443A = "ISO14443A"  # Most common NFC tag type
    ISO14443B = "ISO14443B"  # Less common
    FELICA = "FeliCa"        # Sony's NFC technology
    ISO15693 = "ISO15693"    # Vicinity cards
```

## Command Line Tools

### Validation Script

```bash
# Run detection accuracy validation
uv run python utils/validate_detection_accuracy.py

# Custom validation parameters
uv run python utils/validate_detection_accuracy.py --samples 200 --output-dir validation_results

# Example output:
# Validation complete! Results saved to validation_results/validation_20250731_123456
# Overall Accuracy: 94.5%
# Real-time Requirement: PASS (<500ms)
```

### Demo Scenarios Script

```bash
# Run comprehensive demonstration
uv run python demo_scenarios.py --scenario comprehensive

# Run specific scenarios
uv run python demo_scenarios.py --scenario normal
uv run python demo_scenarios.py --scenario replay
uv run python demo_scenarios.py --scenario jamming
uv run python demo_scenarios.py --scenario brute_force

# Save events to file
uv run python demo_scenarios.py --scenario comprehensive --output demo_events.json
```

## Integration with Detection System

### Validation Pipeline

```python
async def run_validation_pipeline():
    # 1. Generate synthetic test data
    validator = DetectionAccuracyValidator()
    test_data = await validator.generate_test_dataset(100)
    
    # 2. Process through detection system
    from detection.event_logic import analyze_event
    results = []
    
    for event in test_data:
        enriched_event = analyze_event(event)
        results.append(enriched_event)
    
    # 3. Calculate accuracy metrics
    accuracy_results = await validator.evaluate_detection_accuracy(100)
    
    # 4. Generate reports
    validator.generate_confusion_matrix("confusion_matrix.png")
    validator.save_results_to_file(accuracy_results, "validation_report.md")
    
    return accuracy_results
```

### Continuous Validation

```python
async def continuous_validation():
    """Run periodic validation to ensure system performance."""
    while True:
        # Run validation every hour
        await asyncio.sleep(3600)
        
        try:
            results = await run_validation_pipeline()
            accuracy = results["accuracy_metrics"]["overall_accuracy"]
            
            if accuracy < 0.9:
                print(f"WARNING: Accuracy dropped to {accuracy:.2%}")
            else:
                print(f"Validation PASS: {accuracy:.2%} accuracy")
                
        except Exception as e:
            print(f"Validation error: {e}")
```

## Best Practices

### Validation Guidelines

1. **Regular Validation**: Run validation after any detection algorithm changes
2. **Sufficient Sample Size**: Use at least 100 samples for reliable metrics
3. **Balanced Dataset**: Include representative samples of all attack types
4. **Performance Testing**: Validate real-time processing requirements
5. **Confusion Matrix Analysis**: Review per-class performance metrics
6. **Continuous Monitoring**: Implement periodic validation in production

### Demo Scenario Guidelines

1. **Realistic Timing**: Use appropriate delays between events
2. **Progressive Complexity**: Start with simple scenarios, build to complex
3. **Clear Transitions**: Provide clear indicators between scenario phases
4. **Comprehensive Coverage**: Include all major attack types
5. **Repeatable Results**: Ensure scenarios produce consistent outputs
6. **Documentation**: Document scenario purpose and expected outcomes

### Signal Constant Management

1. **Centralized Definitions**: Use signal_constants.py for all parameters
2. **Manufacturer Accuracy**: Ensure manufacturer parameters are realistic
3. **Frequency Validation**: Verify frequencies match regional standards
4. **Modulation Consistency**: Maintain consistent modulation definitions
5. **Version Control**: Track changes to signal parameters
6. **Documentation**: Document source of parameter values

## Troubleshooting

### Common Validation Issues

1. **Low Accuracy**: Check detection algorithm parameters and thresholds
2. **Performance Issues**: Optimize signal processing for real-time requirements
3. **Inconsistent Results**: Ensure deterministic test data generation
4. **Missing Dependencies**: Install required packages (sklearn, matplotlib)

### Demo Scenario Issues

1. **Timing Problems**: Adjust sleep intervals for realistic demonstration
2. **Event Generation Errors**: Check synthetic event generation functions
3. **Scenario Failures**: Verify all required imports and dependencies
4. **Output Format Issues**: Ensure JSON serialization compatibility

### Signal Constant Issues

1. **Frequency Conflicts**: Verify frequency assignments match standards
2. **Manufacturer Errors**: Cross-reference with automotive documentation
3. **Modulation Mismatches**: Ensure modulation types are correctly assigned
4. **Import Errors**: Check module imports and circular dependencies

## Example Usage

### Complete Validation Workflow

```python
async def main():
    print("Starting comprehensive validation...")
    
    # 1. Run accuracy validation
    validator = DetectionAccuracyValidator()
    results = await validator.evaluate_detection_accuracy(200)
    
    accuracy = results["accuracy_metrics"]["overall_accuracy"]
    print(f"Detection Accuracy: {accuracy:.2%}")
    
    # 2. Run demo scenarios
    scenario = ComprehensiveDemoScenario()
    demo_events = await scenario.run()
    print(f"Generated {len(demo_events)} demo events")
    
    # 3. Save results
    validator.save_results_to_file(results, "validation_results.md")
    
    with open("demo_events.json", "w") as f:
        json.dump(demo_events, f, indent=2)
    
    print("Validation complete!")

if __name__ == "__main__":
    asyncio.run(main())
```