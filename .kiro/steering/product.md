# Product Overview

This is an **Automotive Security Capstone Project (2025)** - a proof-of-concept system for monitoring and detecting suspicious automotive RF/NFC wireless activity.

## Core Purpose
- Real-time detection and classification of automotive wireless threats
- Educational/research project for 4th year cybersecurity students
- Hardware-based security monitoring using RTL-SDR and Raspberry Pi Pico W

## Key Components
- **RF Detection**: RTL-SDR V4 dongle captures and processes radio signals
- **Event Processing**: Python backend analyzes signals and detects automotive security events
- **Real-time Monitoring**: CLI dashboard provides live visualization of threats
- **Hardware Alerting**: Raspberry Pi Pico W handles physical alerts (LEDs, NFC)

## Target Use Cases
- Automotive security research and education
- Real-time threat detection demonstrations
- POC for automotive wireless security monitoring
- Student capstone project showcase

## Architecture Philosophy
- **Minimal MVP approach**: No web API or database required
- **TCP-based event streaming**: Simple, direct communication between components
- **Hardware-first design**: Built around RTL-SDR and Pico W capabilities
- **Demo-friendly**: Supports mock mode for presentations without hardware