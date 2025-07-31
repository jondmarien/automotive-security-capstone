# RTL-SDR NFC Integration Test Plan

## Test Objective
Verify that the NFC correlation activation system correctly activates NFC scanning when high-threat RF events are detected, manages correlation state and timeouts, provides LED indicators for NFC correlation mode, and implements correlation event data structures for communication with the backend.

## Test Environment
- Raspberry Pi Pico W with PN532 NFC module
- RTL-SDR dongle with backend signal processing server
- Test NFC tags/cards
- WiFi network for Pico W connectivity

## Test Cases

### Test Case 1: NFC Correlation Activation on High-Threat RF Events
**Objective**: Verify that NFC scanning is activated when high-threat RF events are detected

**Preconditions**:
- Pico W client is running and connected to backend server
- NFC module is properly initialized
- No active correlation mode

**Steps**:
1. Send a high-threat RF event (threat_level > 0.7) from backend to Pico W
2. Observe LED indicators for NFC correlation activation
3. Verify correlation activation event is sent to backend
4. Check that NFC scanning is active

**Expected Results**:
- LED_NFC turns on
- Correlation activation event sent to backend
- NFC scanning becomes active
- Correlation timer starts

### Test Case 2: NFC Correlation Timeout
**Objective**: Verify that NFC correlation mode times out correctly

**Preconditions**:
- NFC correlation mode is active
- Correlation timer is running

**Steps**:
1. Wait for correlation timeout period (30 seconds)
2. Observe LED indicators
3. Verify timeout event is sent to backend

**Expected Results**:
- LED_NFC turns off after timeout
- Timeout event sent to backend
- Correlation mode deactivated

### Test Case 3: NFC Detection During Correlation Mode
**Objective**: Verify that NFC detections during correlation mode generate correlated events

**Preconditions**:
- NFC correlation mode is active
- Active RF threat is stored

**Steps**:
1. Present NFC tag to PN532 reader during correlation mode
2. Observe LED indicators for correlation detection
3. Verify correlated security event is sent to backend

**Expected Results**:
- Visual indication of correlation (LED_NFC and LED_ALERT blinking)
- Correlated security event sent to backend with both RF threat and NFC data
- LED_NFC returns to on state after correlation indication

### Test Case 4: NFC Detection Outside Correlation Mode
**Objective**: Verify that NFC detections outside correlation mode generate regular events

**Preconditions**:
- NFC correlation mode is not active

**Steps**:
1. Present NFC tag to PN532 reader
2. Observe LED indicators
3. Verify regular NFC detection event is sent to backend

**Expected Results**:
- Standard NFC LED indication
- Regular NFC detection event sent to backend

## Test Data Collection
- Log all events sent to and received from backend
- Record LED state changes
- Capture timestamps for all events
- Document any errors or unexpected behavior

## Success Criteria
- All test cases pass as expected
- No system crashes or unexpected behavior
- Events are properly formatted and contain required data
- LED indicators provide clear visual feedback
- Correlation timeout functions correctly
