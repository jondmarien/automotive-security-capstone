"""
simple_performance_monitor.py

Lightweight performance monitoring for automotive security demonstrations.
Tracks key metrics without the complexity of enterprise-scale monitoring.

This module provides simple, demonstration-focused performance monitoring:
- Signal processing latency tracking
- Detection accuracy counters
- Basic system health monitoring
- Memory usage tracking (optional)
- Dashboard-friendly metrics display

Designed for capstone demonstrations and educational purposes.
"""

import time
import threading
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Simple performance metrics for demonstration purposes."""
    
    # Processing metrics
    signals_processed: int = 0
    events_generated: int = 0
    threats_detected: int = 0
    
    # Timing metrics
    average_processing_latency_ms: float = 0.0
    peak_processing_latency_ms: float = 0.0
    total_processing_time_ms: float = 0.0
    
    # Detection accuracy
    key_fob_detections: int = 0
    replay_attacks_detected: int = 0
    jamming_attacks_detected: int = 0
    brute_force_attacks_detected: int = 0
    
    # System health
    system_uptime_seconds: float = 0.0
    memory_usage_mb: float = 0.0
    rtl_sdr_connected: bool = False
    pico_w_connected: bool = False
    
    # Performance tracking
    last_update_time: float = field(default_factory=time.time)

class SimplePerformanceMonitor:
    """
    Lightweight performance monitor for automotive security demonstrations.
    
    Tracks essential metrics without enterprise complexity:
    - Processing latency and throughput
    - Detection accuracy counters
    - System health indicators
    - Memory usage (if available)
    """
    
    def __init__(self, history_size: int = 100):
        """
        Initialize the performance monitor.
        
        Args:
            history_size: Number of historical data points to keep
        """
        self.history_size = history_size
        self.start_time = time.time()
        
        # Current metrics
        self.metrics = PerformanceMetrics()
        
        # Historical data for trends
        self.latency_history = deque(maxlen=history_size)
        self.throughput_history = deque(maxlen=history_size)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Processing time tracking
        self._processing_times = deque(maxlen=50)  # Last 50 processing times
        
        logger.info("SimplePerformanceMonitor initialized")
    
    def record_signal_processed(self, processing_time_ms: float = 0.0):
        """Record a processed signal with optional timing."""
        with self._lock:
            self.metrics.signals_processed += 1
            
            if processing_time_ms > 0:
                self._processing_times.append(processing_time_ms)
                self.metrics.total_processing_time_ms += processing_time_ms
                
                # Update latency metrics
                if processing_time_ms > self.metrics.peak_processing_latency_ms:
                    self.metrics.peak_processing_latency_ms = processing_time_ms
                
                # Calculate average latency
                if self._processing_times:
                    self.metrics.average_processing_latency_ms = sum(self._processing_times) / len(self._processing_times)
                
                # Add to history for trends
                self.latency_history.append(processing_time_ms)
    
    def record_event_generated(self, event_type: str = "unknown"):
        """Record an event generation with type classification."""
        with self._lock:
            self.metrics.events_generated += 1
            
            # Classify event types for demonstration
            if "key_fob" in event_type.lower():
                self.metrics.key_fob_detections += 1
            elif "replay" in event_type.lower():
                self.metrics.replay_attacks_detected += 1
                self.metrics.threats_detected += 1
            elif "jamming" in event_type.lower():
                self.metrics.jamming_attacks_detected += 1
                self.metrics.threats_detected += 1
            elif "brute_force" in event_type.lower():
                self.metrics.brute_force_attacks_detected += 1
                self.metrics.threats_detected += 1
    
    def update_system_health(self, 
                           rtl_sdr_connected: bool = False,
                           pico_w_connected: bool = False,
                           memory_usage_mb: Optional[float] = None):
        """Update system health indicators."""
        with self._lock:
            self.metrics.rtl_sdr_connected = rtl_sdr_connected
            self.metrics.pico_w_connected = pico_w_connected
            self.metrics.system_uptime_seconds = time.time() - self.start_time
            
            if memory_usage_mb is not None:
                self.metrics.memory_usage_mb = memory_usage_mb
            else:
                # Try to get memory usage if psutil is available
                try:
                    import psutil
                    import os
                    process = psutil.Process(os.getpid())
                    self.metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
                except ImportError:
                    # Fallback if psutil not available
                    self.metrics.memory_usage_mb = 0.0
            
            self.metrics.last_update_time = time.time()
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics for display."""
        with self._lock:
            # Calculate throughput (events per minute)
            uptime_minutes = max(self.metrics.system_uptime_seconds / 60, 0.1)  # Avoid division by zero
            events_per_minute = self.metrics.events_generated / uptime_minutes
            
            return {
                # Processing performance
                'signals_processed': self.metrics.signals_processed,
                'events_generated': self.metrics.events_generated,
                'events_per_minute': round(events_per_minute, 1),
                'average_latency_ms': round(self.metrics.average_processing_latency_ms, 1),
                'peak_latency_ms': round(self.metrics.peak_processing_latency_ms, 1),
                
                # Detection accuracy
                'threats_detected': self.metrics.threats_detected,
                'key_fob_detections': self.metrics.key_fob_detections,
                'replay_attacks': self.metrics.replay_attacks_detected,
                'jamming_attacks': self.metrics.jamming_attacks_detected,
                'brute_force_attacks': self.metrics.brute_force_attacks_detected,
                
                # System health
                'uptime_seconds': round(self.metrics.system_uptime_seconds, 1),
                'uptime_formatted': self._format_uptime(self.metrics.system_uptime_seconds),
                'memory_usage_mb': round(self.metrics.memory_usage_mb, 1),
                'rtl_sdr_status': 'Connected' if self.metrics.rtl_sdr_connected else 'Disconnected',
                'pico_w_status': 'Connected' if self.metrics.pico_w_connected else 'Disconnected',
                
                # Performance indicators
                'performance_status': self._get_performance_status(),
                'last_update': self.metrics.last_update_time
            }
    
    def get_dashboard_summary(self) -> str:
        """Get a concise summary for dashboard footer display."""
        metrics = self.get_current_metrics()
        
        # Create concise status string
        status_parts = []
        
        # Processing performance
        if metrics['average_latency_ms'] > 0:
            status_parts.append(f"Latency: {metrics['average_latency_ms']}ms")
        
        # Detection summary - NOTE: Events counter removed to avoid duplication with CLI dashboard
        # The CLI dashboard handles the events counter separately
        
        # System health
        health_indicators = []
        if metrics['rtl_sdr_status'] == 'Connected':
            health_indicators.append('RTL-SDR')
        if metrics['pico_w_status'] == 'Connected':
            health_indicators.append('Pico W')
        
        if health_indicators:
            status_parts.append(f"HW: {', '.join(health_indicators)}")
        
        # Memory usage (if significant)
        if metrics['memory_usage_mb'] > 10:
            status_parts.append(f"Mem: {metrics['memory_usage_mb']}MB")
        
        return ' | '.join(status_parts) if status_parts else 'Monitoring...'
    
    def get_threats_summary(self) -> str:
        """Get threats summary for dashboard display."""
        metrics = self.get_current_metrics()
        
        if metrics['threats_detected'] > 0:
            return f"Threats: {metrics['threats_detected']}"
        else:
            return ""
    
    def get_detailed_report(self) -> Dict[str, Any]:
        """Get detailed performance report for analysis."""
        metrics = self.get_current_metrics()
        
        return {
            'summary': metrics,
            'trends': {
                'latency_trend': list(self.latency_history)[-10:],  # Last 10 measurements
                'throughput_trend': list(self.throughput_history)[-10:],
            },
            'analysis': {
                'performance_grade': self._calculate_performance_grade(),
                'bottlenecks': self._identify_bottlenecks(),
                'recommendations': self._get_recommendations()
            }
        }
    
    def reset_metrics(self):
        """Reset all metrics (useful for demo restarts)."""
        with self._lock:
            self.metrics = PerformanceMetrics()
            self.latency_history.clear()
            self.throughput_history.clear()
            self._processing_times.clear()
            self.start_time = time.time()
            logger.info("Performance metrics reset")
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes}m {int(seconds % 60)}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
    
    def _get_performance_status(self) -> str:
        """Get overall performance status."""
        if self.metrics.average_processing_latency_ms == 0:
            return "Initializing"
        elif self.metrics.average_processing_latency_ms < 50:
            return "Excellent"
        elif self.metrics.average_processing_latency_ms < 100:
            return "Good"
        elif self.metrics.average_processing_latency_ms < 200:
            return "Fair"
        else:
            return "Slow"
    
    def _calculate_performance_grade(self) -> str:
        """Calculate overall performance grade."""
        score = 100
        
        # Deduct points for high latency
        if self.metrics.average_processing_latency_ms > 100:
            score -= 20
        elif self.metrics.average_processing_latency_ms > 200:
            score -= 40
        
        # Deduct points for high memory usage
        if self.metrics.memory_usage_mb > 500:
            score -= 10
        elif self.metrics.memory_usage_mb > 1000:
            score -= 20
        
        # Bonus points for threat detection
        if self.metrics.threats_detected > 0:
            score += 5
        
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _identify_bottlenecks(self) -> List[str]:
        """Identify potential performance bottlenecks."""
        bottlenecks = []
        
        if self.metrics.average_processing_latency_ms > 200:
            bottlenecks.append("High signal processing latency")
        
        if self.metrics.memory_usage_mb > 500:
            bottlenecks.append("High memory usage")
        
        if not self.metrics.rtl_sdr_connected:
            bottlenecks.append("RTL-SDR not connected")
        
        return bottlenecks
    
    def _get_recommendations(self) -> List[str]:
        """Get performance improvement recommendations."""
        recommendations = []
        
        if self.metrics.average_processing_latency_ms > 100:
            recommendations.append("Consider reducing signal processing complexity")
        
        if self.metrics.memory_usage_mb > 500:
            recommendations.append("Monitor memory usage for potential leaks")
        
        if self.metrics.signals_processed > 0 and self.metrics.events_generated == 0:
            recommendations.append("Check detection thresholds - no events generated")
        
        return recommendations

# Global instance for easy access
_global_monitor: Optional[SimplePerformanceMonitor] = None

def get_performance_monitor() -> SimplePerformanceMonitor:
    """Get the global performance monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = SimplePerformanceMonitor()
    return _global_monitor

def reset_performance_monitor():
    """Reset the global performance monitor."""
    global _global_monitor
    if _global_monitor is not None:
        _global_monitor.reset_metrics()
    else:
        _global_monitor = SimplePerformanceMonitor()