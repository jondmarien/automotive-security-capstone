#!/usr/bin/env python3
"""
Test CLI dashboard event scrolling functionality
"""

import asyncio
import json
from datetime import datetime
from cli_dashboard import render_dashboard
from rich.console import Console

def create_test_events():
    """Create test events for scrolling test."""
    events = []
    
    # Create 10 test events with different types and threats
    event_types = [
        ("key_fob_transmission", "Benign"),
        ("replay_attack", "Malicious"),
        ("jamming_attack", "Malicious"),
        ("tpms_transmission", "Benign"),
        ("brute_force_attack", "Suspicious"),
        ("key_fob_transmission", "Benign"),
        ("nfc_detection", "Suspicious"),
        ("relay_attack", "Malicious"),
        ("key_fob_transmission", "Benign"),
        ("unknown_signal", "Suspicious")
    ]
    
    for i, (event_type, threat) in enumerate(event_types):
        event = {
            "timestamp": f"23:4{i:01d}:{i*5:02d}",
            "type": event_type,
            "threat": threat,
            "source": "RTL-SDR",
            "details": f"Test event {i+1} - {event_type}",
            "frequency": 433920000 + i * 1000,
            "rssi": -50 - i,
            "signal_strength": 0.8 - i * 0.05,
            "confidence": 0.9 - i * 0.02,
            "technical_evidence": [
                {
                    "type": "signal_analysis",
                    "details": {
                        "frequency": 433920000 + i * 1000,
                        "bandwidth": 20000,
                        "modulation": "FSK",
                        "rssi": -50 - i,
                        "snr": 15 - i
                    }
                },
                {
                    "type": "threat_indicators",
                    "details": {
                        "pattern": f"Pattern {i+1}: Suspicious timing",
                        "indicator": f"Indicator {i+1}: Unusual frequency"
                    }
                }
            ]
        }
        events.append(event)
    
    return events

def test_event_scrolling():
    """Test event scrolling functionality."""
    print("🎯 Testing CLI Dashboard Event Scrolling")
    print("=" * 50)
    
    console = Console()
    events = create_test_events()
    
    # Test different selected event indices
    test_indices = [-1, -3, -5, -10]  # Latest, 3rd from end, 5th from end, oldest
    
    for idx in test_indices:
        print(f"\\n📍 Testing selected_event_idx = {idx}")
        
        # Render dashboard with specific selected event
        dashboard = render_dashboard(
            events=events,
            selected_event=None,  # Let it use selected_event_idx
            status_text="Testing event scrolling",
            console=console,
            selected_event_idx=idx
        )
        
        # Get the selected event for verification
        if idx != -1 and abs(idx) <= len(events):
            selected_event = events[idx]
        else:
            selected_event = events[-1]
        
        print(f"   Selected event: {selected_event['type']} at {selected_event['timestamp']}")
        print(f"   Threat level: {selected_event['threat']}")
        print(f"   Technical evidence available: {'technical_evidence' in selected_event}")
        
        # Verify the signal analysis would show this event's data
        if 'technical_evidence' in selected_event:
            # Find signal_analysis in the technical evidence list
            signal_analysis = None
            for evidence in selected_event['technical_evidence']:
                if evidence.get('type') == 'signal_analysis':
                    signal_analysis = evidence['details']
                    break
            
            if signal_analysis:
                print(f"   Signal frequency: {signal_analysis['frequency']} Hz")
                print(f"   RSSI: {signal_analysis['rssi']} dBm")
    
    print(f"\\n✅ Event scrolling test completed!")
    print(f"   • Created {len(events)} test events")
    print(f"   • Tested {len(test_indices)} different scroll positions")
    print(f"   • Each position should show different signal analysis data")
    
    print(f"\\n💡 To test interactively:")
    print(f"   1. Run: uv run python cli_dashboard.py --mock")
    print(f"   2. Use Up/Down arrow keys to scroll through events")
    print(f"   3. Watch the 'Signal Analysis' and 'Technical Evidence' panels")
    print(f"   4. They should update to show data for the highlighted event")
    
    return True

if __name__ == "__main__":
    test_event_scrolling()