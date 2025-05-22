"""In-memory data access layer for the edge device."""
import time
from collections import defaultdict, deque
from typing import Any, Deque, Dict, List, Optional


class EdgeDAO:
    """In-memory data store for the edge device.
    
    This provides a simple in-memory storage solution that can be replaced
    with a proper database in production.
    """
    
    def __init__(self, max_packets: int = 1000, max_alerts: int = 100):
        """Initialize the in-memory store.
        
        Args:
            max_packets: Maximum number of packets to store
            max_alerts: Maximum number of alerts to store
        """
        self.max_packets = max_packets
        self.max_alerts = max_alerts
        self.packets: Deque[Dict[str, Any]] = deque(maxlen=max_packets)
        self.alerts: Deque[Dict[str, Any]] = deque(maxlen=max_alerts)
        self.metrics: Dict[str, Any] = {}
        self.packet_count = 0
        self.alert_count = 0
        self.start_time = time.time()
    
    async def save_packet(self, packet: Dict[str, Any]) -> None:
        """Save a packet to the store.
        
        Args:
            packet: Packet data to save
        """
        self.packets.append(packet)
        self.packet_count += 1
    
    async def get_recent_packets(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent packets.
        
        Args:
            limit: Maximum number of packets to return
            
        Returns:
            List of packet dictionaries
        """
        return list(reversed(list(self.packets)[-limit:]))
    
    async def save_alert(self, alert: Dict[str, Any]) -> None:
        """Save an alert to the store.
        
        Args:
            alert: Alert data to save
        """
        self.alerts.append(alert)
        self.alert_count += 1
    
    async def get_recent_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent alerts.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert dictionaries
        """
        return list(reversed(list(self.alerts)[-limit:]))
    
    async def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update device metrics.
        
        Args:
            metrics: Dictionary of metric names and values
        """
        self.metrics.update(metrics)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Retrieve current metrics.
        
        Returns:
            Dictionary of current metrics
        """
        return {
            'packets': {
                'count': len(self.packets),
                'max': self.max_packets,
                'total': self.packet_count
            },
            'alerts': {
                'count': len(self.alerts),
                'max': self.max_alerts
            }
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the data store.
        
        Returns:
            Dictionary containing statistics
        """
        return {
            'packet_count': self.packet_count,
            'alert_count': self.alert_count,
            'uptime_seconds': time.time() - self.start_time,
            'current_packets': len(self.packets),
            'current_alerts': len(self.alerts),
            'max_packets': self.max_packets,
            'max_alerts': self.max_alerts
        }
    
    async def clear_all(self) -> None:
        """Clear all stored data."""
        self.packets.clear()
        self.alerts.clear()
        self.alert_count = 0
        self.packet_count = 0