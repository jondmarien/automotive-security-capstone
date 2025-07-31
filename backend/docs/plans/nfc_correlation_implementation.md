# NFC Correlation System Implementation Plan

## Overview

The NFC Correlation System enhances the automotive security POC by implementing multi-modal attack detection that correlates RF-based attacks with NFC physical proximity events. This document outlines the implementation approach, technical requirements, and integration strategy.

## 1. Hardware Requirements

### Components:
- **Raspberry Pi Pico W**: Central controller with WiFi connectivity
- **PN532 NFC Module**: Connected via SPI interface for proximity detection
- **RTL-SDR V4**: For RF signal capture (existing component)
- **LED Indicators**: For visual status and alerts

### Connection Diagram:
```
Pico W           PN532 NFC Module
---------------------------------
GP18 (SCK)  ---> SCK
GP19 (MOSI) ---> MOSI
GP16 (MISO) ---> MISO
GP17 (CS)   ---> SS
3.3V        ---> VCC
GND         ---> GND
```

### LED Connections:
```
Pico W           LEDs
---------------------------------
GP10        ---> Alert LED (Red)
GP11        ---> Status LED (Green)
GP12        ---> NFC Correlation LED (Blue)
```

## 2. Software Architecture

### MicroPython Components:
- **AutomotiveSecurityPico Class**: Core controller class enhanced with NFC correlation capabilities
- **NFC Module Driver**: Interface for PN532 module using SPI
- **Event Generation System**: Creates and sends detection events to the server
- **Correlation Logic**: Activates NFC scanning on high-threat RF detections
- **Timeout Handling**: Automatically deactivates correlation mode after timeout

### Key Methods:
- `activate_nfc_correlation()`: Activates correlation mode when high-threat RF events occur
- `nfc_correlation_timeout()`: Handles automatic timeout for correlation mode
- `handle_nfc_detection()`: Processes NFC detections with contextual awareness
- `create_correlated_security_event()`: Generates enhanced security events for correlated detections

## 3. Event Structure

### NFC Correlation Activation Event:
```json
{
  "type": "nfc_correlation_activated",
  "timestamp": 1721939551.432,
  "detection_count": 1,
  "threat_types": ["replay_attack"]
}
```

### NFC Correlation Timeout Event:
```json
{
  "type": "nfc_correlation_timeout",
  "timestamp": 1721939581.783,
  "reason": "timeout"
}
```

### Correlated Security Event:
```json
{
  "type": "correlated_security_event",
  "event_id": "correlated_1721939562_15",
  "timestamp": 1721939562.341,
  "rf_threat": {
    "event_type": "replay_attack",
    "threat_level": 0.9
  },
  "nfc_detection": {
    "type": "nfc_detection",
    "timestamp": 1721939562.341,
    "uid": ["0x1", "0x2", "0x3", "0x4"]
  },
  "correlation_type": "rf_nfc_proximity_attack",
  "threat_level": 1.0,
  "technical_evidence": {
    "rf_evidence": {},
    "nfc_evidence": {},
    "correlation_evidence": {}
  },
  "recommended_action": "immediate_security_investigation"
}
```

## 4. Implementation Steps

1. **Hardware Setup**:
   - Configure SPI interface for PN532 module
   - Set up LEDs for visual indicators
   - Test basic NFC reading functionality

2. **Core NFC Functionality**:
   - Implement asynchronous NFC tag reading
   - Create event structure for NFC detections
   - Establish connection to server for event transmission

3. **Correlation System**:
   - Add correlation activation logic based on RF threat level
   - Implement timeout mechanism with configurable duration
   - Create specialized event structures for correlation events

4. **Event Processing**:
   - Enhance server to handle new event types
   - Update dashboard to display correlation events with priority
   - Implement storage for correlation evidence

5. **Testing**:
   - Develop comprehensive test suite for NFC correlation
   - Validate timeout functionality
   - Test correlation activation under various threat scenarios
   - Verify correlated security event generation

## 5. Configuration Parameters

| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| `CORRELATION_TIMEOUT` | 30 seconds | Duration for correlation mode before automatic timeout |
| `CORRELATION_THRESHOLD` | 0.7 | Minimum RF threat level to activate correlation |
| `NFC_SCAN_INTERVAL` | 0.5 seconds | Time between NFC scans during correlation mode |
| `NFC_MAX_UID_LENGTH` | 7 | Maximum UID length to process |
| `SERVER_RECONNECT_ATTEMPTS` | 5 | Attempts to reconnect to server before giving up |

## 6. Testing Plan

### Unit Tests:
- Test NFC tag reading in isolation
- Test correlation activation logic
- Test timeout functionality
- Test event generation for various scenarios

### Integration Tests:
- Test end-to-end flow with mock RF threats
- Test dashboard display of correlated events
- Test system behavior with network disruptions
- Test performance under continuous operation

### Performance Metrics:
- Time from RF detection to correlation activation
- NFC scan rate during correlation mode
- Memory usage during correlation operations
- Event transmission latency
- False positive/negative rates for correlated attacks

## 7. Deployment Strategy

1. **Development Phase**:
   - Implement core functionality on development hardware
   - Use mock RF threats for testing
   - Develop visualization for correlation events

2. **Testing Phase**:
   - Deploy to test environment
   - Generate simulated attacks
   - Measure and tune performance

3. **Production Deployment**:
   - Package firmware for Pico W
   - Update dashboard for production
   - Document configuration parameters
   - Create user guide for interpreting correlation events

## 8. Future Enhancements

- **Machine Learning Integration**: Use ML to improve correlation accuracy
- **Extended Correlation Window**: Add variable correlation windows based on threat patterns
- **Multiple Sensor Fusion**: Incorporate other sensors (GPS, accelerometer) for richer context
- **Mobile App Alerts**: Push critical correlation events to mobile app
- **Correlation History**: Store historical correlation patterns for trend analysis

## 9. Security Considerations

- **Event Encryption**: Encrypt sensitive correlation data in transit
- **Authentication**: Ensure only authorized devices can send correlation events
- **Threat Model**: Update threat model to include multi-modal attacks
- **Data Privacy**: Handle NFC UIDs with appropriate privacy measures
- **Tamper Resistance**: Add physical security measures for production deployment
