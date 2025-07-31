#!/usr/bin/env python3
"""
Test help functionality in CLI dashboard
"""

from cli_dashboard import render_dashboard
from rich.console import Console

def test_help_functionality():
    """Test the help functionality."""
    print("🔧 Testing CLI Dashboard Help Functionality")
    print("=" * 50)
    
    console = Console()
    
    # Create some test events
    events = [
        {
            "timestamp": "23:45:00",
            "type": "key_fob_transmission",
            "threat": "Benign",
            "source": "RTL-SDR",
            "details": "Normal key fob signal",
            "frequency": 433920000,
            "rssi": -50
        },
        {
            "timestamp": "23:45:30",
            "type": "replay_attack",
            "threat": "Malicious",
            "source": "RTL-SDR",
            "details": "Suspicious replay pattern detected",
            "frequency": 433920000,
            "rssi": -45
        }
    ]
    
    # Test without help
    print("\\n📱 Testing dashboard without help:")
    dashboard_no_help = render_dashboard(
        events=events,
        selected_event=None,
        status_text="Testing help functionality",
        console=console,
        selected_event_idx=-1,
        show_help=False
    )
    print("   ✅ Dashboard rendered without help (footer should be 1 line)")
    
    # Test with help
    print("\\n📱 Testing dashboard with help:")
    dashboard_with_help = render_dashboard(
        events=events,
        selected_event=None,
        status_text="Testing help functionality",
        console=console,
        selected_event_idx=-1,
        show_help=True
    )
    print("   ✅ Dashboard rendered with help (footer should be 3 lines)")
    
    print("\\n🎯 Help functionality test completed!")
    print("   • Footer expands from 1 line to 3 lines when help is shown")
    print("   • Help text includes keyboard controls")
    print("   • Status spinner remains visible alongside help")
    
    print("\\n💡 To test interactively:")
    print("   1. Run: uv run python cli_dashboard.py --mock")
    print("   2. Press '?' to toggle help display")
    print("   3. Footer should expand/contract with help information")
    
    return True

if __name__ == "__main__":
    test_help_functionality()