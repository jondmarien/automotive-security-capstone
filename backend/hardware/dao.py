"""In-memory data access layer for the edge device."""
import time
from collections import defaultdict, deque
from typing import Any, Deque, Dict, List


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
        self._packets: Deque[Dict[str, Any]] = deque(maxlen=max_packets)
        self._alerts: Deque[Dict[str, Any]] = deque(maxlen=max_alerts)
        self._packet_counts: Dict[str, int] = defaultdict(int)
    
    async def save_packet(self, packet: Dict[str, Any]) -> str:
        """Save a packet to the store.
        
        Args:
            packet: Packet data to save
            
        Returns:
            str: Unique ID for the saved packet
        """
        packet_id = f"pkt_{len(self._packets)}_{time.time()}"
        packet['id'] = packet_id
        packet['timestamp'] = packet.get('timestamp', time.time())
        self._packets.append(packet)
        self._packet_counts['total'] += 1
        return packet_id
    
    async def save_alert(self, alert: Dict[str, Any]) -> str:
        """Save a security alert to the store.
        
        Args:
            alert: Alert data to save
            
        Returns:
            str: Unique ID for the saved alert
        """
        alert_id = f"alert_{len(self._alerts)}_{time.time()}"
        alert['id'] = alert_id
        alert['timestamp'] = alert.get('timestamp', time.time())
        self._alerts.append(alert)
        return alert_id
    
    async def get_recent_packets(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent packets.
        
        Args:
            limit: Maximum number of packets to return
            
        Returns:
            List of recent packets, most recent first
        """
        # Return most recent packets first (reverse order)
        return list(reversed(list(self._packets)[-limit:]))
    
    async def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent security alerts.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of recent alerts, most recent first
        """
        # Return most recent alerts first (reverse order)
        return list(reversed(list(self._alerts)[-limit:]))
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get storage metrics.
        
        Returns:
            Dictionary containing storage metrics
        """
        return {
            'packets': {
                'count': len(self._packets),
                'max': self.max_packets,
                'total': self._packet_counts.get('total', 0)
            },
            'alerts': {
                'count': len(self._alerts),
                'max': self.max_alerts
            }
        }
    
    async def clear_all(self) -> None:
        """Clear all stored data."""
        self._packets.clear()
        self._alerts.clear()
        self._packet_counts.clear()
