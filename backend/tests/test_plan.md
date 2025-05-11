# Testing & Validation Plan

This plan describes how to verify the functionality, reliability, and compliance of the automotive security dongle. Each section explains the purpose of the tests and how to perform them.

## 1. Functional Validation

- **Test RF detection with known 315/433 MHz signals:**
  - Use RF signal generators or actual automotive keyfobs to transmit at 315/433 MHz.
  - Confirm that the dongle detects these signals and logs/alerts as expected.
- **Test NFC detection with standard 13.56 MHz tags:**
  - Present a variety of NFC tags/cards to the PN532 module.
  - Verify that tag presence is detected and processed correctly.
- **Simulate relay attacks and verify detection:**
  - Use relay attack tools or signal repeaters to simulate real relay attacks.
  - Check that the anomaly detection logic triggers a 'critical' alert.

## 2. Power Consumption

- **Measure current draw during idle, detection, and alert transmission:**
  - Use a USB current meter to monitor power usage in all operating modes.
- **Ensure total draw <500mA:**
  - This is essential for safe operation from vehicle USB ports.

## 3. Environmental Testing

- **Operate in vehicle at high/low temperatures:**
  - Test the dongle in both hot and cold conditions to ensure stability.
- **Test with engine on/off (noise/interference):**
  - Evaluate performance with the vehicle running and stopped, as power and noise conditions change.
- **Test with nearby RF sources (garage door, tire sensors):**
  - Confirm that the dongle does not produce false positives from common vehicle RF sources.

## 4. Compliance

- **Ensure emissions within FCC Part 15 limits:**
  - Use a spectrum analyzer to verify that the dongle does not emit excessive RF noise.
- **Document test results:**
  - Keep records of all compliance and validation tests for future reference.

## 5. Debugging Techniques

- **Use serial debug output for signal logs:**
  - Enable serial logging to monitor real-time system status and events.
- **Log all alerts and anomalies:**
  - Store logs for later analysis and troubleshooting.
- **Use test scripts in `tests/` to automate scenarios:**
  - Automate repetitive test cases to ensure consistent results and speed up validation.
