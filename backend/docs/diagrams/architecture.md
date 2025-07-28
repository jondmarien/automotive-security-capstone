# Automotive Security POC - System Architecture

## High-Level Architecture Overview

```mermaid
graph TB
    %% Hardware Layer
    subgraph HW ["🔧 Hardware Layer"]
        RTL[RTL-SDR V4<br/>RF Signal Capture]
        PICO[Raspberry Pi Pico W<br/>Alert Controller]
    end
    
    %% Processing Layer  
    subgraph PROC ["⚙️ Signal Processing Layer"]
        TCP_SRV[RTL-TCP Server<br/>Port 1234<br/>IQ Data Stream]
        SIG_PROC[RF Signal Processing<br/>Engine<br/>Event Detection]
        AUTO_ANALYZER[Automotive Signal<br/>Analyzer<br/>FSK/TPMS Detection<br/>Real-time IQ Analysis]
        HIST_BUFFER[Signal History<br/>Buffer<br/>Temporal Analysis<br/>5-min Rolling Buffer]
        DETECT[Enhanced Threat<br/>Detection Engine<br/>Replay/Jamming/Brute Force<br/>Advanced Pattern Recognition]
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
    EVENT_SRV -->|TCP<br/>Events| DASH
    EVENT_SRV -->|WiFi TCP<br/>Events| WIFI
    WIFI -->|Alert<br/>Commands| ALERTS
    ALERTS -->|Physical<br/>Alerts| PICO
    
    %% Styling
    classDef hardware fill:#f8cecc,stroke:#b85450,stroke-width:2px,color:#000
    classDef processing fill:#d5e8d4,stroke:#82b366,stroke-width:2px,color:#000
    classDef communication fill:#fff2cc,stroke:#d6b656,stroke-width:2px,color:#000
    
    class RTL,PICO hardware
    class TCP_SRV,SIG_PROC,DETECT processing
    class EVENT_SRV,DASH,WIFI,ALERTS communication
```

## Detailed Component Architecture

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
    H --> I
    H --> J
    
    %% Styling
    classDef rfChain fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,color:#000
    classDef eventDist fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef clients fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    
    class A,B,C,D,E rfChain
    class F,G,H eventDist
    class I,J,K clients
```

## Data Flow & Protocol Stack

```mermaid
sequenceDiagram
    participant RTL as RTL-SDR V4
    participant TCP_SRV as RTL-TCP Server
    participant SIG as Signal Processor
    participant DET as Threat Detector
    participant EVT as Event Server
    participant DASH as Dashboard
    participant PICO as Pico W Client
    
    Note over RTL,PICO: System Initialization
    RTL->>TCP_SRV: USB Connection (Raw RF Data)
    TCP_SRV->>SIG: TCP Stream (IQ Samples, Port 1234)
    EVT->>DASH: TCP Connection (Port 8888)
    EVT->>PICO: WiFi TCP Connection (Port 8888)
    
    Note over RTL,PICO: Real-time Operation Loop
    loop Continuous Monitoring
        RTL->>TCP_SRV: RF Signal Capture
        TCP_SRV->>SIG: IQ Data Stream
        SIG->>DET: Processed Signal Data
        
        alt Threat Detected
            DET->>EVT: Security Event
            EVT->>DASH: Event Notification
            EVT->>PICO: Alert Command
            PICO->>PICO: Trigger LED/NFC Alert
        else Normal Operation
            DET->>EVT: Status Update
        end
    end
```

## Network & Port Configuration

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
    
    classDef port fill:#fff2cc,stroke:#d6b656,stroke-width:2px,color:#000
    classDef device fill:#f8cecc,stroke:#b85450,stroke-width:2px,color:#000
    
    class PORT_1234,PORT_8888 port
    class PICO_IP,COMPUTER_IP device
```

## Technology Stack Overview

| Layer | Component | Technology | Purpose |
|-------|-----------|------------|---------|
| **Hardware** | RTL-SDR V4 | USB RF Dongle | RF signal capture and digitization |
| **Hardware** | Raspberry Pi Pico W | MicroPython | WiFi-enabled alert controller |
| **Processing** | RTL-TCP Server | C/C++ Binary | Raw IQ data streaming |
| **Processing** | Signal Bridge | Python + NumPy | Signal processing and analysis |
| **Processing** | Automotive Analyzer | Python + SciPy | Advanced automotive signal analysis with FSK/TPMS detection |
| **Processing** | Signal History Buffer | Python + Threading | Thread-safe temporal analysis and replay detection (5-min buffer) |
| **Processing** | Threat Detection Engine | Python + Pydantic | Enhanced security event classification with confidence scoring |
| **Communication** | Event Server | Python + asyncio | TCP event distribution |
| **Interface** | CLI Dashboard | Python + Rich | Real-time monitoring interface |
| **Alerts** | NFC/LED System | MicroPython | Physical security notifications |

## Key Features

### 🔒 Security Monitoring
- Real-time RF signal analysis
- Automotive protocol detection
- Threat level classification
- Event logging and reporting

### 🚀 Performance
- Low-latency event processing
- Concurrent client support
- Efficient TCP streaming
- Hardware-accelerated alerts

### 🛠️ Development Features
- Mock mode for testing
- Modular architecture
- Comprehensive logging
- Hardware abstraction layer

### 📊 Monitoring & Visualization
- Rich terminal dashboard
- Real-time event display
- Threat level indicators
- Historical event logging

## Deployment Architecture

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
    
    classDef dev fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef demo fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef prod fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    
    class DEV_PC,DEV_RTL,DEV_PICO dev
    class DEMO_PC,DEMO_PROJ demo
    class PROD_PC,PROD_RTL,PROD_PICO prod
```