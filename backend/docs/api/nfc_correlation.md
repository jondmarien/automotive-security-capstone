# Pico W NFC Correlation System API

## Overview

The Pico W NFC Correlation System introduces multi-modal attack detection by correlating RF-based automotive attacks with NFC physical proximity events. This system enables sophisticated attack detection by identifying situations where both remote RF signals and physical proximity (via NFC) occur together, potentially indicating a coordinated attack.

## System Components

### AutomotiveSecurityPico

**File**: `pico/main.py`

The AutomotiveSecurityPico class has been enhanced with NFC correlation capabilities, enabling the detection of coordinated RF-NFC attacks.

#### NFC Correlation Methods

##### activate_nfc_correlation()

```python
async def activate_nfc_correlation(self, detections)
```

**Parameters**:
- `detections` (list): List of high-threat RF detections that triggered correlation mode

**Description**:
- Activates NFC correlation mode when high-threat RF events are detected
- Sets a correlation timeout to automatically deactivate the mode after a configurable period
- Sends a correlation activation event to the server
- Provides visual indication of active correlation mode via LEDs

##### nfc_correlation_timeout()

```python
async def nfc_correlation_timeout(self)
```

**Description**:
- Handles the automatic timeout of NFC correlation mode
- Deactivates correlation mode after the configured timeout period
- Sends a correlation timeout event to the server
- Resets visual indicators when correlation mode ends

##### handle_nfc_detection()

```python
async def handle_nfc_detection(self, uid)
```

**Parameters**:
- `uid` (bytes): Unique identifier of the detected NFC tag/card

**Description**:
- Processes NFC tag/card detections
- Checks if detection occurred during active RF correlation mode
- If correlation is active, generates enhanced correlated security events
- Otherwise, sends regular NFC detection events
- Provides visual feedback for NFC detection

##### create_correlated_security_event()

```python
def create_correlated_security_event(self, rf_threat, nfc_detection)
```

**Parameters**:
- `rf_threat` (dict): RF threat detection that triggered correlation mode
- `nfc_detection` (dict): NFC detection data

**Returns**:
- `dict`: Comprehensive correlated security event with technical evidence

**Description**:
- Creates combined RF-NFC threat event structures with technical evidence
- Calculates threat escalation based on both RF and NFC characteristics
- Collects technical evidence for multi-modal attacks
- Generates appropriate recommended actions for correlated threats

## Event Structures

### NFC Correlation Activation Event

Sent when high-threat RF events activate correlation mode:

```json
{
  "type": "nfc_correlation_activated",
  "timestamp": 1721939551.432,
  "detection_count": 1,
  "threat_types": ["key_fob_transmission"]
}
```

### NFC Correlation Timeout Event

Sent when correlation mode times out without an NFC detection:

```json
{
  "type": "nfc_correlation_timeout",
  "timestamp": 1721939581.783,
  "reason": "timeout"
}
```

### NFC Detection Event (Standard)

Regular NFC detection event outside correlation mode:

```json
{
  "type": "nfc_detection",
  "timestamp": 1721939562.341,
  "uid": ["0x1", "0x2", "0x3", "0x4"],
  "uid_length": 4,
  "detection_context": "automotive_monitoring"
}
```

### Correlated Security Event

Enhanced security event when RF and NFC activities are correlated:

```json
{
  "type": "correlated_security_event",
  "event_id": "correlated_1721939562_15",
  "timestamp": 1721939562.341,
  "rf_threat": {
    "event_type": "replay_attack",
    "threat_level": 0.9,
    "frequency_mhz": 315.0,
    "power_db": -45.2,
    "timing_analysis": {"burst_interval_ms": 150},
    "modulation": "fsk"
  },
  "nfc_detection": {
    "type": "nfc_detection",
    "timestamp": 1721939562.341,
    "uid": ["0x1", "0x2", "0x3", "0x4"],
    "uid_length": 4,
    "detection_context": "automotive_monitoring"
  },
  "correlation_type": "rf_nfc_proximity_attack",
  "threat_level": 1.0,
  "threat_category": "multi_modal_attack",
  "technical_evidence": {
    "rf_evidence": {
      "signal_type": "replay_attack",
      "frequency": 315000000,
      "power_db": -45.2
    },
    "nfc_evidence": {
      "uid": ["0x1", "0x2", "0x3", "0x4"],
      "uid_length": 4
    },
    "correlation_evidence": {
      "time_delta_seconds": 12.3,
      "proximity_confidence": 0.95
    }
  },
  "recommended_action": "immediate_security_investigation_required",
  "confidence_score": 0.95
}
```

## Usage Examples

### Handling Correlated Security Events

```python
def process_security_event(event):
    if event['type'] == 'correlated_security_event':
        # Handle multi-modal attack with highest priority
        print(f"CRITICAL: Multi-modal attack detected!")
        print(f"RF Threat: {event['rf_threat']['event_type']}")
        print(f"NFC UID: {event['nfc_detection']['uid']}")
        print(f"Threat Level: {event['threat_level']}")
        print(f"Recommended Action: {event['recommended_action']}")
        
        # Access technical evidence
        evidence = event['technical_evidence']
        print(f"Time between RF and NFC: {evidence['correlation_evidence']['time_delta_seconds']} seconds")
        
        # Take appropriate action based on recommended_action
        if event['recommended_action'] == 'immediate_security_investigation_required':
            trigger_security_alarm()
            notify_security_team(event)
```

### Setting Up NFC Correlation (Pico W)

```python
# Initialize AutomotiveSecurityPico
pico = AutomotiveSecurityPico()

# Connect to WiFi and server
pico.connect_wifi()
await pico.connect_to_server(SERVER_IP, SERVER_PORT)

# Start monitoring tasks
asyncio.create_task(pico.process_server_messages())
asyncio.create_task(pico.monitor_nfc())

# NFC correlation will automatically activate when high-threat RF events are detected
```

## Testing

Tests for the NFC correlation system are provided in:

```bash
# Test NFC correlation functionality
python -m pytest tests/test_pico_nfc_correlation.py -v
```

Test cases validate:
- Correlation activation on high-threat events
- Correlation timeout functionality
- Correlated vs. regular NFC detections
- Correlated security event generation
- Threat level escalation logic

## Integration Notes

### Hardware Requirements

- **Raspberry Pi Pico W** with WiFi connectivity
- **PN532 NFC Module** connected via SPI interface
- Proper power supply and interface wiring (see hardware docs)

### Configuration

The correlation system can be configured through several parameters:

```python
# Configuration options (in pico/main.py)
self.correlation_timeout = 30  # seconds until correlation mode times out
```

### Integration with Other Systems

The correlated security events can be processed by:

1. **CLI Dashboard** - Displays correlated events with highest priority
2. **Security Monitoring Systems** - Process events via TCP for advanced response
3. **Logging Systems** - Record comprehensive evidence for forensic analysis

This API enables sophisticated multi-modal attack detection by correlating RF signals with physical proximity events, significantly enhancing automotive security capabilities.
