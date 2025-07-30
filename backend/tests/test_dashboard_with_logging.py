#!/usr/bin/env python3
"""
Quick test of CLI dashboard with logging (non-interactive)
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logging_config import setup_dashboard_logging, log_event_detection, log_dashboard_action

async def test_dashboard_logging_integration():
    """Test the dashboard logging integration without full UI."""
    print("🔧 Testing CLI Dashboard Logging Integration")
    print("=" * 50)
    
    # Setup logging like the dashboard does
    logger = setup_dashboard_logging(
        log_level="INFO",
        log_name="dashboard",
        console_output=False
    )
    
    # Simulate dashboard startup
    logger.info("CLI Dashboard starting up")
    logger.info("Arguments: {'mock': True, 'detailed': True}")
    logger.info("Using mock event generator for demo/testing")
    
    # Simulate some events
    test_events = [
        {
            'type': 'key_fob_transmission',
            'threat': 'Benign',
            'timestamp': '00:01:00',
            'source': 'RTL-SDR'
        },
        {
            'type': 'replay_attack',
            'threat': 'Malicious',
            'timestamp': '00:01:15',
            'source': 'RTL-SDR'
        },
        {
            'type': 'jamming_attack',
            'threat': 'Critical',
            'timestamp': '00:01:30',
            'source': 'RTL-SDR'
        }
    ]
    
    # Log the events
    for event in test_events:
        log_event_detection(logger, event, "Test Integration")
        await asyncio.sleep(0.1)  # Small delay
    
    # Simulate user actions
    log_dashboard_action(logger, "navigation", "Up arrow - selected event index: -2")
    log_dashboard_action(logger, "help_toggle", "Help display enabled")
    log_dashboard_action(logger, "navigation", "End key - jumped to latest event")
    log_dashboard_action(logger, "quit", "User initiated dashboard shutdown")
    
    # Simulate shutdown
    logger.info("CLI Dashboard shutting down")
    logger.info("=" * 60)
    
    print("✅ Logging integration test completed!")
    
    # Check the log file was created
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_dir = Path("logs") / f"dashboard-{current_date}"
    
    if log_dir.exists():
        log_files = list(log_dir.glob("dashboard-*.log"))
        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
        
        print(f"📄 Latest log file: {latest_log}")
        print(f"📊 File size: {latest_log.stat().st_size / 1024:.1f} KB")
        
        # Show last few lines
        with open(latest_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"\\n📋 Last 5 log entries:")
            for line in lines[-5:]:
                print(f"   {line.strip()}")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_dashboard_logging_integration())