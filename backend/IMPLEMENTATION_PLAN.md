You are an expert embedded systems engineer specializing in automotive cybersecurity with extensive experience in RF signal detection systems. Help me implement a low-cost automotive security dongle using RTL-SDR for 315-433 MHz detection and a PN532 module for 13.56 MHz NFC detection.

My project specifications:
- Budget-friendly alternative to expensive SDR hardware (~$50 total BOM vs $300+)
- USB-powered dongle that plugs into a vehicle's lighter socket
- Must detect suspicious RF signals that could indicate relay attacks
- Alerts sent via mobile app (BLE or Wi-Fi communication)
- Non-invasive design (no vehicle integration required)
- Microcontroller: Raspberry Pi Pico

Please provide a detailed implementation plan with the following elements:

1. **Hardware Integration:**
   - Circuit design for connecting RTL-SDR via USB and PN532 via SPI/I2C to the Raspberry Pi Pico
   - Power management considerations for vehicle USB port (voltage regulation, surge protection)
   - Antenna selection and placement for optimal RF reception at both frequency ranges
   - Compact enclosure design considerations for dashboard mounting

2. **Firmware Development:**
   - Core algorithms for processing RTL-SDR data using rtl_433 tool
   - PN532 NFC detection implementation using libnfc
   - Signal strength threshold determination for anomaly detection
   - Pattern recognition for relay attack signatures
   - BLE/Wi-Fi communication protocol with the mobile app
   - Power management and sleep modes

3. **Signal Processing:**
   - Code examples for filtering out environmental noise
   - Implementation of RSSI thresholds (-60dBm baseline)
   - Statistical methods to reduce false positives
   - Data structures for storing signal patterns and history
   - Real-world testing methodology

4. **Alert System:**
   - Algorithm for classifying threats (severity levels)
   - Alert data format (JSON) with encryption
   - Notification queue management
   - Retry logic for failed transmissions

5. **Testing Framework:**
   - Validation test procedures for both frequency ranges
   - Simulated attack scenarios
   - Power consumption measurement
   - Environmental testing (temperature, interference)
   - Regulatory compliance considerations

Include code snippets, component pinouts, circuit diagrams (described in text format), and debugging techniques. The solution should focus on reliability, performance, and minimizing false positives while maintaining a small form factor suitable for a vehicle environment.
