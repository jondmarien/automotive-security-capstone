"""Main module for the automotive security edge device."""
import time
from typing import Any, Dict, Optional

from .dao import EdgeDAO
from .log_utils import logger
from .packet import Packet
from .report_logic import SecurityAnalyzer
from .signal_filter import SignalFilter


class EdgeDevice:
    """Main class for the automotive security edge device.
    
    This class ties together all the components of the edge device:
    - Signal capture and filtering
    - Security analysis
    - Data storage
    - Logging
    """
    
    def __init__(self, device_id: str = "default_device"):
        """Initialize the edge device.
        
        Args:
            device_id: Unique identifier for this device
        """
        self.device_id = device_id
        self.signal_filter = SignalFilter()
        self.security_analyzer = SecurityAnalyzer()
        self.dao = EdgeDAO()
        self.running = False
        self.packet_count = 0
        self.alert_count = 0
        
        # Initialize logger
        logger.info(f"Edge device {device_id} initialized")
    
    async def process_packet(self, rssi: int, freq: float, payload: bytes) -> Optional[Dict[str, Any]]:  # noqa: E501
        """Process a single RF packet.
        
        Args:
            rssi: Signal strength in dBm
            freq: Frequency in MHz
            payload: Raw packet data
            
        Returns:
            Dict containing processing results, or None if packet was filtered out
        """
        # Create packet object
        packet = Packet(rssi=rssi, freq=freq, payload=payload)
        
        # Apply signal filtering
        if not self.signal_filter.should_accept(packet):
            logger.debug(f"Packet filtered out: {packet.signature}")
            return None
        
        # Save packet to storage
        packet_data = packet.to_dict()
        await self.dao.save_packet(packet_data)
        self.packet_count += 1
        
        # Perform security analysis
        report = self.security_analyzer.analyze_packet(packet)
        
        # If threat detected, save alert
        if report.threat_level != 'BENIGN':
            alert_data = report.to_dict()
            alert_data['device_id'] = self.device_id
            await self.dao.save_alert(alert_data)
            self.alert_count += 1
            logger.warning(f"Security alert: {report.reason}", extra={"packet": packet_data})  # noqa: E501
        
        # Log packet processing
        logger.debug(
            f"Processed packet: {packet.signature}",
            extra={
                "rssi": rssi,
                "freq": freq,
                "payload": payload.hex()
            }
        )
        
        return {
            "packet": packet_data,
            "threat_detected": report.threat_level != 'BENIGN',
            "threat_level": report.threat_level,
            "reason": report.reason
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the edge device.
        
        Returns:
            Dictionary containing device status information
        """
        metrics = await self.dao.get_metrics()
        signal_metrics = self.signal_filter.get_signal_metrics()
        security_metrics = self.security_analyzer.get_metrics()
        
        return {
            "device_id": self.device_id,
            "status": "running" if self.running else "stopped",
            "packets_processed": self.packet_count,
            "alerts_generated": self.alert_count,
            "storage_metrics": metrics,
            "signal_metrics": signal_metrics,
            "security_metrics": security_metrics,
            "timestamp": time.time()
        }
    
    async def start(self) -> None:
        """Start the edge device."""
        if self.running:
            logger.warning("Device is already running")
            return
        
        self.running = True
        logger.info("Edge device started")
    
    async def stop(self) -> None:
        """Stop the edge device."""
        if not self.running:
            logger.warning("Device is not running")
            return
        
        self.running = False
        logger.info("Edge device stopped")
    
    async def reset(self) -> None:
        """Reset the edge device state."""
        await self.dao.clear_all()
        self.packet_count = 0
        self.alert_count = 0
        logger.info("Edge device state reset")
