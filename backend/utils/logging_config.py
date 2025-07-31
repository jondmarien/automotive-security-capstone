#!/usr/bin/env python3
"""
Logging Configuration for Automotive Security CLI Dashboard

This module provides centralized logging configuration with organized file structure:
- Creates date-based subdirectories: logs/dashboard-2025-07-29/
- Creates timestamped log files: dashboard-23-45-30.log
- Supports multiple log levels and formatters
- Integrates with CLI dashboard for comprehensive event logging

Usage:
    from utils.logging_config import setup_dashboard_logging
    logger = setup_dashboard_logging()
    logger.info("Dashboard started")
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class DashboardLogFormatter(logging.Formatter):
    """Custom formatter for dashboard logs with enhanced formatting."""
    
    def __init__(self):
        # Enhanced format with more context
        super().__init__(
            fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | %(message)s',
            datefmt='%H:%M:%S'
        )
    
    def format(self, record):
        # Add custom fields for automotive security context
        if hasattr(record, 'event_type'):
            record.msg = f"[{record.event_type}] {record.msg}"
        if hasattr(record, 'threat_level'):
            record.msg = f"{record.msg} (Threat: {record.threat_level})"
        
        return super().format(record)


def create_log_directory(base_dir: str = "logs", log_name: str = "dashboard") -> Path:
    """
    Create organized log directory structure.
    
    Args:
        base_dir: Base directory for logs (default: "logs")
        log_name: Name prefix for log directory (default: "dashboard")
    
    Returns:
        Path to the created log directory
    
    Directory structure:
        logs/
        ├── dashboard-2025-07-29/
        │   ├── dashboard-09-30-15.log
        │   ├── dashboard-10-45-22.log
        │   └── dashboard-11-20-08.log
        └── dashboard-2025-07-30/
            ├── dashboard-08-15-30.log
            └── dashboard-09-45-12.log
    """
    # Get current date for directory name
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_dir_name = f"{log_name}-{current_date}"
    
    # Create full path
    log_dir = Path(base_dir) / log_dir_name
    log_dir.mkdir(parents=True, exist_ok=True)
    
    return log_dir


def get_log_filename(log_name: str = "dashboard") -> str:
    """
    Generate timestamped log filename.
    
    Args:
        log_name: Base name for log file (default: "dashboard")
    
    Returns:
        Timestamped filename like "dashboard-23-45-30.log"
    """
    current_time = datetime.now().strftime("%H-%M-%S")
    return f"{log_name}-{current_time}.log"


def setup_dashboard_logging(
    log_level: str = "INFO",
    log_name: str = "dashboard",
    base_dir: str = "logs",
    console_output: bool = True
) -> logging.Logger:
    """
    Set up comprehensive logging for the CLI dashboard.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_name: Base name for log files and directories
        base_dir: Base directory for log storage
        console_output: Whether to also log to console
    
    Returns:
        Configured logger instance
    
    Example:
        logger = setup_dashboard_logging(log_level="DEBUG", log_name="dashboard")
        logger.info("Dashboard started successfully")
        logger.warning("High threat level detected", extra={'threat_level': 'MALICIOUS'})
    """
    # Create log directory
    log_dir = create_log_directory(base_dir, log_name)
    
    # Generate log filename
    log_filename = get_log_filename(log_name)
    log_file_path = log_dir / log_filename
    
    # Create logger
    logger = logging.getLogger("automotive_security_dashboard")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create custom formatter
    formatter = DashboardLogFormatter()
    
    # File handler with rotation-like behavior (new file each run)
    file_handler = logging.FileHandler(log_file_path, mode='w', encoding='utf-8')
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler (optional)
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
        console_handler.setFormatter(logging.Formatter(
            '%(levelname)s: %(message)s'
        ))
        logger.addHandler(console_handler)
    
    # Log the setup information
    logger.info("=" * 60)
    logger.info("AUTOMOTIVE SECURITY CLI DASHBOARD - LOGGING STARTED")
    logger.info("=" * 60)
    logger.info(f"Log Level: {log_level.upper()}")
    logger.info(f"Log Directory: {log_dir}")
    logger.info(f"Log File: {log_filename}")
    logger.info(f"Console Output: {console_output}")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    return logger


def log_event_detection(logger: logging.Logger, event: dict, context: str = ""):
    """
    Log detection events with structured and pretty formatting.
    
    Args:
        logger: Logger instance
        event: Detection event dictionary
        context: Additional context information
    """
    event_type = event.get('type', 'unknown')
    threat_level = event.get('threat', 'unknown')
    timestamp = event.get('timestamp', datetime.now().strftime('%H:%M:%S'))
    
    # Create pretty formatted message
    event_details = []
    
    # Add basic event info
    event_details.append(f"Type: {event_type}")
    event_details.append(f"Threat: {threat_level}")
    event_details.append(f"Time: {timestamp}")
    
    # Add source if available
    if 'source' in event:
        event_details.append(f"Source: {event['source']}")
    
    # Add frequency if available
    if 'frequency' in event:
        freq_mhz = event['frequency'] / 1e6
        event_details.append(f"Freq: {freq_mhz:.3f}MHz")
    
    # Add RSSI if available
    if 'rssi' in event:
        event_details.append(f"RSSI: {event['rssi']}dBm")
    
    # Add NFC correlation if present
    if event.get('nfc_correlated', False):
        event_details.append("NFC: CORRELATED")
    
    # Create the main message
    formatted_details = " | ".join(event_details)
    
    # Add context if provided
    if context:
        message = f"🚨 EVENT DETECTED: {formatted_details} | Context: {context}"
    else:
        message = f"🚨 EVENT DETECTED: {formatted_details}"
    
    # Add details if available
    if 'details' in event and event['details']:
        message += f" | Details: {event['details']}"
    
    # Log with appropriate level and emoji based on threat
    threat_upper = threat_level.upper()
    if threat_upper in ['MALICIOUS', 'CRITICAL']:
        if threat_upper == 'CRITICAL':
            message = message.replace('🚨', '🔴')  # Red circle for critical
        logger.error(message, extra={
            'event_type': event_type,
            'threat_level': threat_level,
            'event_data': event
        })
    elif threat_upper == 'SUSPICIOUS':
        message = message.replace('🚨', '🟡')  # Yellow circle for suspicious
        logger.warning(message, extra={
            'event_type': event_type,
            'threat_level': threat_level,
            'event_data': event
        })
    else:
        message = message.replace('🚨', '🟢')  # Green circle for benign
        logger.info(message, extra={
            'event_type': event_type,
            'threat_level': threat_level,
            'event_data': event
        })


def log_dashboard_action(logger: logging.Logger, action: str, details: str = ""):
    """
    Log dashboard user actions and system events with pretty formatting.
    
    Args:
        logger: Logger instance
        action: Action performed (e.g., "navigation", "help_toggle", "quit")
        details: Additional details about the action
    """
    # Add appropriate emoji for different actions
    action_emojis = {
        'navigation': '🧭',
        'help_toggle': '❓',
        'quit': '🚪',
        'startup': '🚀',
        'shutdown': '🛑',
        'error': '❌',
        'warning': '⚠️'
    }
    
    emoji = action_emojis.get(action, '🎯')
    
    # Create formatted message
    if details:
        message = f"{emoji} USER ACTION: {action.upper()} | {details}"
    else:
        message = f"{emoji} USER ACTION: {action.upper()}"
    
    logger.info(message)


def log_performance_metrics(logger: logging.Logger, metrics: dict):
    """
    Log performance metrics from the dashboard with pretty formatting.
    
    Args:
        logger: Logger instance
        metrics: Performance metrics dictionary
    """
    # Pretty format the performance metrics
    formatted_metrics = []
    
    # Core performance metrics
    if 'signals_processed' in metrics:
        formatted_metrics.append(f"Signals: {metrics['signals_processed']}")
    if 'events_generated' in metrics:
        formatted_metrics.append(f"Events: {metrics['events_generated']}")
    if 'average_latency_ms' in metrics:
        formatted_metrics.append(f"Avg Latency: {metrics['average_latency_ms']:.1f}ms")
    if 'peak_latency_ms' in metrics:
        formatted_metrics.append(f"Peak Latency: {metrics['peak_latency_ms']:.1f}ms")
    
    # Threat detection metrics
    threat_metrics = []
    if 'threats_detected' in metrics:
        threat_metrics.append(f"Total Threats: {metrics['threats_detected']}")
    if 'replay_attacks' in metrics:
        threat_metrics.append(f"Replay: {metrics['replay_attacks']}")
    if 'jamming_attacks' in metrics:
        threat_metrics.append(f"Jamming: {metrics['jamming_attacks']}")
    if 'brute_force_attacks' in metrics:
        threat_metrics.append(f"Brute Force: {metrics['brute_force_attacks']}")
    
    # System health metrics
    system_metrics = []
    if 'memory_usage_mb' in metrics:
        memory = metrics['memory_usage_mb']
        if memory > 0:
            system_metrics.append(f"Memory: {memory:.1f}MB")
        else:
            system_metrics.append("Memory: N/A")
    if 'uptime_formatted' in metrics:
        system_metrics.append(f"Uptime: {metrics['uptime_formatted']}")
    if 'performance_status' in metrics:
        system_metrics.append(f"Status: {metrics['performance_status']}")
    
    # Hardware status
    hardware_metrics = []
    if 'rtl_sdr_status' in metrics:
        hardware_metrics.append(f"RTL-SDR: {metrics['rtl_sdr_status']}")
    if 'pico_w_status' in metrics:
        hardware_metrics.append(f"Pico W: {metrics['pico_w_status']}")
    
    # Create formatted message
    message_parts = []
    if formatted_metrics:
        message_parts.append(f"Performance: {' | '.join(formatted_metrics)}")
    if threat_metrics:
        message_parts.append(f"Threats: {' | '.join(threat_metrics)}")
    if system_metrics:
        message_parts.append(f"System: {' | '.join(system_metrics)}")
    if hardware_metrics:
        message_parts.append(f"Hardware: {' | '.join(hardware_metrics)}")
    
    # Log the formatted message
    formatted_message = " || ".join(message_parts)
    logger.info(f"📊 PERFORMANCE METRICS: {formatted_message}")
    
    # Also log events per minute if available
    if 'events_per_minute' in metrics:
        logger.debug(f"📈 Event Rate: {metrics['events_per_minute']:.1f} events/min")


def log_system_health(logger: logging.Logger, health_status: dict):
    """
    Log system health information with pretty formatting.
    
    Args:
        logger: Logger instance
        health_status: System health status dictionary
    """
    # Pretty format the system health data
    health_parts = []
    
    # Dashboard state
    if 'total_events' in health_status:
        health_parts.append(f"Total Events: {health_status['total_events']}")
    if 'events_processed' in health_status:
        health_parts.append(f"Processed: {health_status['events_processed']}")
    
    # Navigation state
    if 'selected_event_idx' in health_status:
        idx = health_status['selected_event_idx']
        if idx == -1:
            health_parts.append("View: Latest Event")
        else:
            health_parts.append(f"View: Event Index {idx}")
    
    # UI state
    ui_state = []
    if 'follow_latest' in health_status:
        ui_state.append(f"Auto-Follow: {'ON' if health_status['follow_latest'] else 'OFF'}")
    if 'show_help' in health_status:
        ui_state.append(f"Help: {'VISIBLE' if health_status['show_help'] else 'HIDDEN'}")
    
    if ui_state:
        health_parts.append(f"UI: {' | '.join(ui_state)}")
    
    # Create formatted message
    formatted_message = " | ".join(health_parts)
    logger.info(f"🏥 SYSTEM HEALTH: {formatted_message}")


# Example usage and testing
if __name__ == "__main__":
    # Test the logging configuration
    print("🔧 Testing Dashboard Logging Configuration")
    print("=" * 50)
    
    # Setup logging
    logger = setup_dashboard_logging(log_level="DEBUG", console_output=True)
    
    # Test different log levels
    logger.debug("Debug message: System initialization")
    logger.info("Info message: Dashboard started successfully")
    logger.warning("Warning message: High CPU usage detected")
    logger.error("Error message: Failed to connect to RTL-SDR")
    logger.critical("Critical message: System security breach detected")
    
    # Test event logging
    test_event = {
        'type': 'replay_attack',
        'threat': 'MALICIOUS',
        'timestamp': '23:45:30',
        'source': 'RTL-SDR',
        'frequency': 433920000
    }
    
    log_event_detection(logger, test_event, "CLI Dashboard Test")
    
    # Test dashboard actions
    log_dashboard_action(logger, "navigation", "User pressed Up arrow")
    log_dashboard_action(logger, "help_toggle", "Help display toggled ON")
    
    # Test performance logging
    test_metrics = {
        'latency_ms': 45.2,
        'events_processed': 150,
        'memory_usage_mb': 89.5
    }
    
    log_performance_metrics(logger, test_metrics)
    
    print("\\n✅ Logging test completed!")
    print("Check the logs/ directory for organized log files.")