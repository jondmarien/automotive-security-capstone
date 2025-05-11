# Circuit Integration for Automotive Security Dongle

## Overview

This document describes the pinouts, connections, and power management for integrating the RTL-SDR dongle (for RF detection) and PN532 NFC module (for NFC detection) with the Raspberry Pi Pico microcontroller. This hardware setup enables the dongle to monitor automotive RF and NFC signals for security threats.

## 1. RTL-SDR Integration

- **Connection:**
  - The RTL-SDR is connected to the Raspberry Pi Pico via a USB OTG cable.
  - The Pico acts as the USB host, allowing it to interface with the SDR dongle for 315/433 MHz signal monitoring.
- **Power:**
  - The dongle is powered by the vehicle's USB port (typically 5V).
  - The Pico requires 3.3V, so a voltage regulator is used to step down from 5V to 3.3V.
- **Antenna:**
  - Use an external whip antenna attached to the RTL-SDR for optimal reception.
  - Place the antenna near the dashboard for best coverage of automotive RF signals.
- **Protection:**
  - Add a TVS (transient voltage suppression) diode and a fuse on the USB power line to protect against voltage spikes and overcurrent conditions. This is important for automotive environments where power can be noisy.

## 2. PN532 NFC Module

- **Connection:**
  - Use the SPI interface (recommended for speed and reliability) to connect the PN532 to the Pico.
  - Typical pin mapping:
    - Pico SPI0: SCK (GP18), MOSI (GP19), MISO (GP16), CS (GP17)
    - PN532: Connect to matching SPI pins.
- **Power:**
  - The PN532 operates at 3.3V, supplied by the Pico's voltage regulator.
- **Antenna:**
  - Use the PN532's onboard PCB trace antenna, oriented to face the vehicle interior for best NFC tag detection.

## 3. Power Management

- **Input:**
  - The dongle is powered from the vehicle's USB or lighter port (5V typical).
- **Regulation:**
  - Use a low-dropout (LDO) 3.3V regulator (e.g., MCP1700) to supply clean 3.3V power to the Pico and PN532.
- **Surge Protection:**
  - Place a TVS diode (e.g., SMAJ5.0A) across the 5V and GND lines to absorb voltage spikes.
- **Fuse:**
  - Add a 500mA polyfuse in series with the 5V line for overcurrent protection. This helps prevent damage if a short or fault occurs.

## 4. Enclosure

- **Design:**
  - Use a compact plastic enclosure, vented for heat dissipation.
  - The enclosure should be mountable on the dashboard or in a convenient location inside the vehicle.
  - Ensure antenna ports and USB connectors are accessible.

## 5. Block Diagram (Text)

The following block diagram shows the main power and signal flow:

```sh
[Vehicle USB]--(5V)--[Fuse]--[TVS]--[Pico]--(SPI)--[PN532]
                                 |                |
                              [RTL-SDR]      [Antenna]
```

## Debugging Tips

- Use a USB current meter to verify that the total current draw is less than 500mA (important for vehicle USB ports).
- Check all ground connections for continuity to avoid signal noise and power issues.
- Before installing in a vehicle, test the system with known NFC tags and RF signals to confirm correct operation.
