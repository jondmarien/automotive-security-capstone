# Automotive RF Detection Logic: Event Types & Detection Methods

This document explains how each event type in the Automotive Security Capstone project is detected, both in real (SDR) and mock/demo modes. The system now includes enhanced signal processing capabilities for advanced automotive signal analysis.

---

## **General Approach**
- **RF packets** are analyzed for frequency, timing, payload patterns, and context (e.g., repeated unlocks, signal strength, etc.).
- **Enhanced Signal Processing** uses advanced automotive signal analysis with FSK detection, burst pattern recognition, and temporal correlation.
- **Mock/demo mode** simulates plausible packets and cycles through all event types for demonstration purposes, but uses the same logic structure.
- **Detection logic** is centralized in `backend/detection/event_logic.py` via the `analyze_event()` function.
- **Enhanced detection** is available through `backend/rtl_sdr/enhanced_signal_bridge.py` with advanced threat analysis.

## **Enhanced Signal Processing Architecture**

### **AutomotiveSignalAnalyzer** (`automotive_signal_analyzer.py`)
- **Real-time IQ Analysis**: Advanced FFT-based power spectrum computation
- **Key Fob Detection**: FSK pattern recognition with timing analysis and confidence scoring
- **TPMS Signal Detection**: Tire pressure monitoring system identification
- **Burst Pattern Analysis**: Sophisticated burst timing and interval detection
- **Modulation Classification**: Automatic FSK/ASK/Unknown modulation detection

### **Signal History Buffer** (`signal_history_buffer.py`)
- **Temporal Analysis**: 5-minute rolling buffer for replay attack detection
- **Signal Similarity**: Advanced correlation analysis for duplicate signal detection
- **Thread-safe Operations**: Concurrent access for real-time processing
- **Memory Management**: Efficient buffer management with configurable size limits

### **Enhanced Threat Detection Engine** (`enhanced_signal_bridge.py`)
- **Replay Attack Detection**: Signal similarity analysis with temporal correlation
- **Jamming Detection**: Broadband interference and noise floor analysis
- **Brute Force Detection**: Rate-based attack pattern recognition
- **Confidence Scoring**: Advanced threat confidence calculation

---

## **Event Types & Detection Logic**

### 1. **RF Unlock / RF Lock**
- **Definition:** Legitimate key fob unlock/lock command.
- **Detection:**
  - Recognized by expected RF frequency (e.g., 315/433/868 MHz).
  - Payload matches known unlock/lock command patterns (manufacturer-specific).
  - Signal strength (RSSI) is within normal range.
  - Not repeated in rapid succession (to avoid brute force/replay classification).
  - **Threat Level:** Benign (unless anomalous context is detected).

### 2. **Replay Attack**
- **Definition:** An attacker records a legitimate unlock/lock signal and replays it to gain unauthorized access.
- **Detection:**
  - **Legacy Mode:** Identical or highly similar RF packets detected more than once, outside of expected timing.
  - **Enhanced Mode:** Advanced signal similarity analysis using:
    - Power spectrum correlation (40% weight)
    - Burst timing pattern matching (30% weight)
    - Frequency deviation comparison (20% weight)
    - Signal bandwidth analysis (10% weight)
  - **Temporal Analysis:** Signal history buffer tracks signals for 5 minutes to detect replays
  - **Timing Characteristics:** Replay attacks typically occur 1 second to 5 minutes after original
  - **Confidence Scoring:** Multi-factor confidence calculation with threshold-based detection
  - No rolling code progression (if rolling code is used, see [Rolling code](https://en.wikipedia.org/wiki/Rolling_code)).
  - **Threat Level:** Always Malicious in demo; enhanced logic uses sophisticated similarity analysis.

### 3. **Jamming Attack**
- **Definition:** An attacker transmits noise or signals to block legitimate RF communication (e.g., prevent lock/unlock).
- **Detection:**
  - **Legacy Mode:** Sustained or repeated RF noise detected on the expected frequency bands.
  - **Enhanced Mode:** Advanced jamming detection using `JammingDetector` class:
    - **Noise Floor Analysis:** Detects elevation >10 dB above baseline noise levels with temporal baseline calculation
    - **Broadband Interference:** Spectral flatness analysis (>0.5 threshold) for wideband jamming detection
    - **Pattern Recognition:** Four jamming types detected:
      - **Continuous Jamming:** Sustained high power with low variance (<25 dB²)
      - **Pulse Jamming:** Periodic high-power bursts with regular timing intervals
      - **Sweep Jamming:** Systematic frequency progression with >60% directional consistency
      - **Spot Jamming:** Narrow-band high power with >10:1 peak-to-average ratio (updated threshold)
    - **Confidence Scoring:** Weighted combination of noise elevation (30%), broadband interference (20%), and pattern detection (50%)
    - **Evidence Collection:** Technical proof including affected frequencies, interference duration, and SNR degradation
    - **Temporal Accuracy:** Improved detection using chronologically ordered signal history for baseline calculation
  - High RSSI with no valid payloads.
  - Lock/unlock packets missing or failing during noise bursts.
  - **Threat Level:** Malicious (confidence >90%), Suspicious (confidence >70%), or Benign (confidence ≤70%).

### 4. **Brute Force Attack**
- **Definition:** Repeated attempts to unlock/lock by cycling through possible codes or sending many packets.
- **Detection:**
  - **Legacy Mode:** Multiple unlock/lock attempts detected in rapid succession.
  - **Enhanced Mode:** Rate-based detection using signal history buffer:
    - **Rate Threshold:** >10 signals per minute of same type
    - **Time Window Analysis:** 60-second sliding window for rate calculation
    - **Pattern Analysis:** Inter-signal interval consistency analysis
    - **Confidence Scoring:** Based on rate excess above threshold
  - **Signal History:** Tracks recent signals by type for temporal analysis
  - Payloads differ slightly (code cycling) or repeat with invalid codes.
  - More attempts than normal user behavior would generate.
  - **Threat Level:** Malicious.

### 5. **Unknown**
- **Definition:** RF packet does not match any known pattern or event type.
- **Detection:**
  - Frequency is in automotive band but payload is unrecognized.
  - No match to unlock/lock, replay, brute force, or jamming signatures.
  - **Threat Level:** Always Suspicious (never Malicious or Benign in demo).

### 6. **NFC Scan / NFC Tag Present**
- **Definition:** Near-field communication event, e.g., key card or phone scanned.
- **Detection:**
  - Detected by NFC hardware interface.
  - Payload matches expected NFC tag or scan pattern.
  - **Threat Level:** Benign (unless anomalous context).

---

## **Summary Table**
| Event Type         | Detection Method Highlights                              | Threat Level (Demo) |
|--------------------|---------------------------------------------------------|---------------------|
| RF Unlock/Lock     | Known RF pattern, normal timing, valid RSSI             | Benign              |
| Replay Attack      | Duplicate packet, no rolling code, odd timing           | Malicious           |
| Jamming Attack     | High noise, no valid payloads, comms blocked            | Malicious           |
| Brute Force        | Rapid, repeated attempts, code cycling                  | Malicious           |
| Unknown            | No match to known patterns                              | Suspicious          |
| NFC Scan/Tag       | NFC interface, valid tag pattern                        | Benign              |

---

## **References & Further Reading**
- [Replay attack - Wikipedia](https://en.wikipedia.org/wiki/Replay_attack)
- [Rolling code - Wikipedia](https://en.wikipedia.org/wiki/Rolling_code)
- [Radio jamming - Wikipedia](https://en.wikipedia.org/wiki/Radio_jamming)
- [Brute-force attack - Wikipedia](https://en.wikipedia.org/wiki/Brute-force_attack)
- [Automotive security - Wikipedia](https://en.wikipedia.org/wiki/Automotive_security)

---

**Note:**
- In demo/mock mode, events are cycled for visibility, but logic structure matches real detection code.
- For real deployments, detection can be enhanced with rolling code validation, anomaly detection, and context-aware analysis.