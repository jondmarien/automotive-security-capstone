# Section E: System Architecture

This section provides a comprehensive overview of the automotive security monitoring system architecture, including detailed system design, component interactions, and technical implementation decisions.

## E.1 Architectural Overview

The automotive security monitoring system employs a three-layer architecture designed to separate hardware concerns, signal processing logic, and user interface components. This architectural decision enables independent modification and upgrade of any layer without affecting others, which is crucial for a system that must adapt to new threats and different hardware configurations.

### E.1.1 High-Level System Architecture

```mermaid
graph TB
    %% Hardware Layer
    subgraph HW ["🔧 Hardware Layer"]
        RTL[RTL-SDR V4<br/>RF Signal Capture]
        PICO[Raspberry Pi Pico W<br/>Alert Controller]
        NFC[PN532 NFC Module<br/>Proximity Detection]
    end
    
    %% Processing Layer  
    subgraph PROC ["⚙️ Signal Processing Layer"]
        TCP_SRV[RTL-TCP Server<br/>Port 1234<br/>IQ Data Stream]
        SIG_PROC[RF Signal Processing<br/>Engine<br/>Event Detection]
        AUTO_ANALYZER[Automotive Signal<br/>Analyzer<br/>FSK/TPMS Detection<br/>Real-time IQ Analysis]
        HIST_BUFFER[Signal History<br/>Buffer<br/>Temporal Analysis<br/>5-min Rolling Buffer]
        DETECT[Enhanced Threat<br/>Detection Engine<br/>Replay/Jamming/Brute Force<br/>Advanced Pattern Recognition]
        NFC_CORR[NFC Correlation<br/>System<br/>Multi-Modal Detection]
    end
    
    %% Communication Layer
    subgraph COMM ["📡 Communication & Interface Layer"]
        EVENT_SRV[TCP Event Server<br/>Port 8888<br/>Event Distribution]
        DASH[Real-time Dashboard<br/>Rich Terminal UI<br/>Live Monitoring]
        WIFI[WiFi Communication<br/>TCP Client<br/>Event Reception]
        ALERTS[NFC & LED Alerts<br/>Physical Notifications<br/>Security Warnings]
    end
    
    %% Data Flow
    RTL -->|USB<br/>Raw RF Data| TCP_SRV
    TCP_SRV -->|TCP<br/>IQ Samples| SIG_PROC
    SIG_PROC -->|Complex<br/>Samples| AUTO_ANALYZER
    AUTO_ANALYZER -->|Signal<br/>Features| DETECT
    DETECT -->|Event<br/>History| HIST_BUFFER
    HIST_BUFFER -->|Temporal<br/>Analysis| DETECT
    DETECT -->|Security<br/>Events| EVENT_SRV
    DETECT -->|High Threat<br/>Events| NFC_CORR
    NFC -->|Proximity<br/>Data| NFC_CORR
    NFC_CORR -->|Correlated<br/>Security Events| EVENT_SRV
    EVENT_SRV -->|TCP<br/>Events| DASH
    EVENT_SRV -->|WiFi TCP<br/>Events| WIFI
    WIFI -->|Alert<br/>Commands| ALERTS
    ALERTS -->|Physical<br/>Alerts| PICO
    NFC -.->|Connected to| PICO
```

### E.1.2 Architectural Layers

| Layer | Components | Purpose | Technology Stack |
|-------|------------|---------|------------------|
| **Hardware Layer** | RTL-SDR V4, Pico W, PN532 NFC | RF capture, physical alerts, proximity detection | USB 3.0, WiFi 802.11n, SPI |
| **Processing Layer** | Signal processing, threat detection, correlation | Real-time analysis and threat identification | Python, NumPy, SciPy, asyncio |
| **Communication Layer** | TCP servers, dashboard, event distribution | User interface and system coordination | TCP/IP, Rich terminal UI, JSON |

## E.2 Component Architecture

### E.2.1 Detailed Component Interaction

```mermaid
graph LR
    %% RF Capture & Processing Chain
    subgraph RF_CHAIN ["RF Signal Processing Chain"]
        direction TB
        A[RTL-SDR V4 Dongle] --> B[RTL-TCP Server<br/>Port 1234]
        B --> C[Signal Bridge<br/>IQ Processing]
        C --> C1[Automotive Signal<br/>Analyzer<br/>FSK/TPMS Detection]
        C1 --> D[Enhanced Event<br/>Detection<br/>Pattern Recognition]
        D --> D1[Signal History<br/>Buffer<br/>Temporal Analysis]
        D1 --> E[Threat Detection<br/>Engine<br/>Replay/Jamming/Brute Force]
    end
    
    %% NFC Correlation Chain
    subgraph NFC_CHAIN ["NFC Correlation System"]
        direction TB
        N1[PN532 NFC Module<br/>Proximity Detection]
        N2[NFC Correlation<br/>Activation Logic]
        N3[Multi-Modal<br/>Security Event<br/>Generator]
        
        N1 --> N2
        N2 --> N3
    end
    
    %% Event Distribution
    subgraph EVENT_DIST ["Event Distribution System"]
        direction TB
        F[TCP Event Server<br/>Port 8888]
        G[Event Queue<br/>Management]
        H[Client Connection<br/>Handler]
        
        F --> G
        G --> H
    end
    
    %% Client Systems
    subgraph CLIENTS ["Client Systems"]
        direction TB
        I[CLI Dashboard<br/>Rich Terminal UI]
        J[Pico W TCP Client<br/>WiFi Connection]
        K[Alert System<br/>LEDs & NFC]
        
        J --> K
    end
    
    %% Connections
    E --> F
    E --> N2
    N3 --> F
    H --> I
    H --> J
    J --> N1
```

### E.2.2 Core System Components

#### Hardware Abstraction Layer
- **RTL-SDR Interface** (`hardware/rtl_sdr_interface.py`): Manages RTL-SDR hardware detection, configuration, and health monitoring
- **Pico Connection Manager** (`hardware/pico_connection_manager.py`): Handles Pico W WiFi connections with automatic reconnection
- **Hardware Manager** (`hardware/hardware_manager.py`): Centralized coordination of all hardware components

#### Signal Processing Engine
- **Automotive Signal Analyzer** (`rtl_sdr/automotive_signal_analyzer.py`): Advanced FSK detection and automotive protocol analysis
- **Signal History Buffer** (`rtl_sdr/signal_history_buffer.py`): Thread-safe temporal analysis with 5-minute rolling buffer
- **Enhanced Signal Bridge** (`rtl_sdr/enhanced_signal_bridge.py`): Real-time IQ processing with automotive-specific optimizations

#### Threat Detection System
- **Security Analyzer** (`detection/security_analyzer.py`): Main threat detection engine with pattern recognition
- **Replay Attack Detector** (`detection/replay_attack_detector.py`): Signal similarity analysis for replay detection
- **Jamming Detector** (`detection/jamming_detector.py`): RF interference detection with four pattern types
- **Brute Force Detector** (`rtl_sdr/brute_force_detector.py`): Temporal analysis with escalating threat levels

## E.3 Data Flow and Protocol Stack

### E.3.1 System Operation Sequence

```mermaid
sequenceDiagram
    participant RTL as RTL-SDR V4
    participant TCP_SRV as RTL-TCP Server
    participant SIG as Signal Processor
    participant DET as Threat Detector
    participant EVT as Event Server
    participant DASH as Dashboard
    participant PICO as Pico W Client
    participant NFC as NFC Module
    
    Note over RTL,NFC: System Initialization
    RTL->>TCP_SRV: USB Connection (Raw RF Data)
    TCP_SRV->>SIG: TCP Stream (IQ Samples, Port 1234)
    EVT->>DASH: TCP Connection (Port 8888)
    EVT->>PICO: WiFi TCP Connection (Port 8888)
    PICO->>NFC: Initialize NFC Module
    
    Note over RTL,NFC: Real-time Operation Loop
    loop Continuous Monitoring
        RTL->>TCP_SRV: RF Signal Capture
        TCP_SRV->>SIG: IQ Data Stream
        SIG->>DET: Processed Signal Data
        
        alt High Threat RF Event Detected
            DET->>EVT: Security Event (High Threat)
            EVT->>DASH: Event Notification
            EVT->>PICO: High Threat RF Alert
            PICO->>PICO: Activate NFC Correlation
            PICO->>EVT: NFC Correlation Activated Event
            
            alt NFC Tag Detected During Correlation
                NFC->>PICO: NFC Tag Detection
                PICO->>PICO: Create Correlated Security Event
                PICO->>EVT: Correlated Security Event
                EVT->>DASH: Correlated Attack Notification
                PICO->>PICO: Trigger Critical LED Alert
            else Correlation Timeout
                PICO->>PICO: Deactivate Correlation Mode
                PICO->>EVT: NFC Correlation Timeout Event
            end
            
        else Normal RF Event
            DET->>EVT: Standard Security Event
            EVT->>DASH: Event Notification
            EVT->>PICO: Standard Alert Command
            PICO->>PICO: Trigger Standard LED Alert
        end
        
        alt Standard NFC Detection (No Correlation)
            NFC->>PICO: NFC Tag Detection
            PICO->>EVT: Standard NFC Detection Event
            EVT->>DASH: NFC Detection Notification
        end
    end
```

### E.3.2 Communication Protocols

| Protocol | Port | Purpose | Data Format | Performance |
|----------|------|---------|-------------|-------------|
| RTL-TCP | 1234 | IQ data streaming | Binary IQ samples | High bandwidth (2+ MS/s) |
| Event TCP | 8888 | Security event distribution | JSON messages | Low latency (<50ms) |
| WiFi TCP | 8888 | Pico W communication | JSON events | Reliable delivery |
| USB | N/A | RTL-SDR control | USB 3.0 bulk transfer | Real-time streaming |

## E.4 Network Architecture

### E.4.1 Network Topology

```mermaid
graph TB
    subgraph NETWORK ["Network Configuration"]
        subgraph LOCALHOST ["Localhost (127.0.0.1)"]
            PORT_1234[Port 1234<br/>RTL-TCP Server<br/>IQ Data Stream]
            PORT_8888[Port 8888<br/>Event Distribution<br/>TCP Server]
        end
        
        subgraph WIFI_NET ["WiFi Network"]
            PICO_IP[Pico W<br/>Dynamic IP<br/>TCP Client]
            COMPUTER_IP[Computer<br/>Static/Dynamic IP<br/>TCP Server]
        end
    end
    
    PORT_1234 -.->|Internal| PORT_8888
    PORT_8888 -->|WiFi TCP| PICO_IP
    COMPUTER_IP -.->|Same Host| PORT_8888
```

### E.4.2 Network Design Decisions

**TCP Selection Rationale**: TCP was chosen over UDP for all inter-component communication because security events cannot be lost. The reliability guarantees that TCP provides are essential for a security monitoring system, despite slightly higher latency compared to UDP.

**Port Separation**: The system uses two distinct TCP ports for different communication types:
- **Port 1234**: High-bandwidth IQ data (RTL-TCP standard)
- **Port 8888**: Low-latency security events (custom protocol)

This separation allows optimization of each communication channel for its specific purpose and simplifies debugging and monitoring.

## E.5 Technology Stack and Implementation

### E.5.1 Technology Selection Matrix

| Layer | Component | Technology | Rationale |
|-------|-----------|------------|-----------|
| **Hardware** | RTL-SDR V4 | R828D tuner + RTL2832U | Wide frequency range (500 kHz - 1.75 GHz), automotive coverage |
| **Hardware** | Raspberry Pi Pico W | RP2040 + WiFi | Low power, real-time response, WiFi connectivity |
| **Hardware** | PN532 NFC Module | 13.56 MHz NFC/RFID | Proximity detection, multi-modal attack correlation |
| **Processing** | Signal Processing | Python + NumPy/SciPy | Optimized mathematical operations, development productivity |
| **Processing** | Threat Detection | Python + Pydantic | Type safety, data validation, rapid development |
| **Processing** | Concurrency | Python asyncio | Non-blocking I/O, concurrent client support |
| **Communication** | Event Distribution | TCP/JSON | Reliability, cross-platform compatibility |
| **Interface** | Dashboard | Python Rich | Professional terminal UI, real-time updates |
| **Embedded** | Pico W Firmware | MicroPython | Rapid development, WiFi support, GPIO control |

### E.5.2 Performance Characteristics

| Metric | Target | Achieved | Measurement Method |
|--------|--------|----------|-------------------|
| Signal Processing Latency | <100ms | ~50ms | End-to-end timing analysis |
| Event Distribution Latency | <50ms | ~25ms | TCP timestamp comparison |
| Memory Usage | <100MB | ~75MB | System resource monitoring |
| CPU Usage | <25% | ~15% | Performance profiling |
| Detection Accuracy | >90% | >92% | Validation framework testing |

## E.6 Security Architecture

### E.6.1 Multi-Modal Attack Detection

The system implements sophisticated multi-modal attack detection by correlating RF signals with physical proximity events through NFC:

1. **RF Threat Detection**: Primary detection of suspicious automotive RF signals
2. **NFC Correlation Activation**: High-threat RF events trigger NFC monitoring
3. **Proximity Correlation**: NFC tag detection during active correlation creates correlated security events
4. **Threat Escalation**: Correlated events automatically escalate to CRITICAL threat level

### E.6.2 Threat Classification System

```mermaid
graph TD
    A[RF Signal Detected] --> B{Signal Analysis}
    B --> C[BENIGN: Normal Activity]
    B --> D[SUSPICIOUS: Unusual Pattern]
    B --> E[MALICIOUS: Attack Signature]
    
    E --> F{NFC Correlation Active?}
    F -->|Yes| G{NFC Detection?}
    F -->|No| H[Standard MALICIOUS Event]
    
    G -->|Yes| I[CRITICAL: Correlated Attack]
    G -->|No| J[Correlation Timeout]
    
    I --> K[Multi-Modal Security Event]
    H --> L[Standard Security Event]
    J --> L
```

## E.7 Deployment Architecture

### E.7.1 Deployment Configurations

```mermaid
graph TB
    subgraph DEV ["Development Environment"]
        DEV_PC[Developer PC<br/>Windows/Linux]
        DEV_RTL[RTL-SDR V4<br/>USB Connected]
        DEV_PICO[Pico W<br/>Development Board]
    end
    
    subgraph DEMO ["Demo Environment"]
        DEMO_PC[Demo Laptop<br/>Mock Mode]
        DEMO_PROJ[Projector Display<br/>CLI Dashboard]
    end
    
    subgraph PROD ["Production POC"]
        PROD_PC[Embedded PC<br/>Raspberry Pi 4]
        PROD_RTL[RTL-SDR V4<br/>Automotive Mount]
        PROD_PICO[Pico W<br/>Alert Panel]
    end
    
    DEV_PC --> DEV_RTL
    DEV_PC --> DEV_PICO
    DEMO_PC --> DEMO_PROJ
    PROD_PC --> PROD_RTL
    PROD_PC --> PROD_PICO
```

### E.7.2 Scalability Considerations

The architecture provides multiple paths for scaling and enhancement:

1. **Horizontal Scaling**: Multiple RTL-SDR devices can monitor different frequency bands simultaneously
2. **Distributed Processing**: Signal processing can be distributed across multiple machines
3. **Cloud Integration**: Event data can be forwarded to cloud-based analytics platforms
4. **Hardware Expansion**: Additional sensor types can be integrated through the hardware abstraction layer

## E.8 Development and Testing Architecture

### E.8.1 Testing Framework Integration

The system includes comprehensive testing capabilities integrated into the architecture:

- **Mock Hardware Layer**: Complete hardware simulation for development without physical devices
- **Synthetic Signal Generation**: Realistic signal generation for validation and testing
- **Performance Testing**: Real-time processing validation with <100ms latency requirements
- **Accuracy Validation**: >90% detection accuracy verification with confusion matrix analysis

### E.8.2 Development Features

- **Mock Mode**: Hardware-free operation for demonstrations and development
- **Modular Design**: Independent component development and testing
- **Comprehensive Logging**: Detailed system operation tracking and debugging
- **Error Handling**: Graceful failure handling with automatic recovery

## E.9 Innovation and Technical Achievement

### E.9.1 Novel Architectural Elements

1. **Multi-Modal Correlation**: First implementation of RF-NFC correlation for automotive security
2. **Real-Time SDR Processing**: Custom signal processing pipeline optimized for automotive protocols
3. **Embedded Alert Integration**: Seamless integration of embedded alerts with software-defined radio
4. **Context-Aware Filtering**: Intelligent signal filtering using -60dBm threshold with context awareness

### E.9.2 System Integration Complexity

The architecture successfully integrates multiple complex domains:
- Software-defined radio signal processing
- Real-time threat detection algorithms
- Distributed system communication
- Embedded system programming
- Network protocol implementation
- User interface design

This integration demonstrates advanced systems engineering capabilities and practical cybersecurity implementation skills, creating a cohesive solution that addresses real-world automotive security challenges.

## E.10 Future Architecture Evolution

### E.10.1 Planned Enhancements

1. **Machine Learning Integration**: Enhanced threat detection using ML algorithms
2. **Cloud Analytics**: Integration with cloud-based security analytics platforms
3. **Mobile Interface**: Smartphone app for remote monitoring and alerts
4. **Vehicle Integration**: Direct integration with vehicle CAN bus systems

### E.10.2 Architectural Flexibility

The modular architecture design ensures that future enhancements can be implemented without major system redesign:
- Component interfaces are well-defined and stable
- Network-based communication supports distributed deployment
- Hardware abstraction layer accommodates new sensor types
- Event-driven architecture supports integration with external systems

This architectural foundation provides a robust platform for continued development and deployment in real-world automotive security applications.