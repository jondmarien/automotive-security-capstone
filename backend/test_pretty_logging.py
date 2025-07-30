#!/usr/bin/env python3
"""
Test the pretty logging formatting
"""

import asyncio
from utils.logging_config import (
    setup_dashboard_logging,
    log_event_detection,
    log_dashboard_action,
    log_performance_metrics,
    log_system_health
)

async def test_pretty_logging():
    """Test the pretty logging formatting."""
    print("🎨 Testing Pretty Logging Formatting")
    print("=" * 50)
    
    # Setup logging
    logger = setup_dashboard_logging(
        log_level="DEBUG",
        log_name="dashboard",
        console_output=False
    )
    
    # Test event detection with different threat levels
    test_events = [
        {
            'type': 'key_fob_transmission',
            'threat': 'Benign',
            'timestamp': '00:15:30',
            'source': 'RTL-SDR',
            'frequency': 433920000,
            'rssi': -50,
            'details': 'Normal key fob unlock signal'
        },
        {
            'type': 'replay_attack',
            'threat': 'Suspicious',
            'timestamp': '00:15:45',
            'source': 'RTL-SDR',
            'frequency': 433920000,
            'rssi': -45,
            'details': 'Potential replay pattern detected'
        },
        {
            'type': 'jamming_attack',
            'threat': 'Malicious',
            'timestamp': '00:16:00',
            'source': 'RTL-SDR',
            'frequency': 433920000,
            'rssi': -30,
            'details': 'Active jamming detected'
        },
        {
            'type': 'brute_force_attack',
            'threat': 'Critical',
            'timestamp': '00:16:15',
            'source': 'RTL-SDR',
            'frequency': 433920000,
            'rssi': -35,
            'nfc_correlated': True,
            'details': 'Multi-modal attack with NFC correlation'
        }
    ]
    
    # Log the events
    for event in test_events:
        log_event_detection(logger, event, "Pretty Logging Test")
        await asyncio.sleep(0.1)
    
    # Test dashboard actions
    log_dashboard_action(logger, "navigation", "Up arrow - selected event index: -2")
    log_dashboard_action(logger, "help_toggle", "Help display enabled")
    log_dashboard_action(logger, "quit", "User initiated dashboard shutdown")
    
    # Test performance metrics
    test_metrics = {
        'signals_processed': 45,
        'events_generated': 23,
        'average_latency_ms': 67.3,
        'peak_latency_ms': 89.1,
        'threats_detected': 8,
        'replay_attacks': 3,
        'jamming_attacks': 2,
        'brute_force_attacks': 1,
        'memory_usage_mb': 125.7,
        'uptime_formatted': '5m 23s',
        'performance_status': 'Good',
        'rtl_sdr_status': 'Connected',
        'pico_w_status': 'Connected',
        'events_per_minute': 45.2
    }
    
    log_performance_metrics(logger, test_metrics)
    
    # Test system health
    test_health = {
        'total_events': 23,
        'events_processed': 45,
        'selected_event_idx': -3,
        'follow_latest': False,
        'show_help': True
    }
    
    log_system_health(logger, test_health)
    
    print("✅ Pretty logging test completed!")
    print("Check the latest log file for formatted output.")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_pretty_logging())