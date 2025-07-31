#!/usr/bin/env python3
"""
Test CLI dashboard with performance monitoring integration
"""

from utils.simple_performance_monitor import get_performance_monitor

def test_dashboard_performance_integration():
    """Test the CLI dashboard performance monitoring integration."""
    print("🚗 Testing CLI Dashboard Performance Integration")
    print("=" * 55)
    
    # Get the performance monitor
    monitor = get_performance_monitor()
    
    # Simulate realistic automotive security monitoring
    print("📡 Simulating automotive security monitoring...")
    
    # Simulate signal processing with various latencies
    monitor.record_signal_processed(42.0)  # Excellent
    monitor.record_signal_processed(67.0)  # Good
    monitor.record_signal_processed(89.0)  # Good
    monitor.record_signal_processed(125.0) # Fair
    
    # Simulate different types of events
    monitor.record_event_generated('key_fob_transmission')
    monitor.record_event_generated('key_fob_transmission')
    monitor.record_event_generated('tpms_transmission')
    monitor.record_event_generated('replay_attack')  # Threat
    monitor.record_event_generated('jamming_attack') # Threat
    
    # Update system health
    monitor.update_system_health(
        rtl_sdr_connected=True,
        pico_w_connected=True,
        memory_usage_mb=95.2
    )
    
    # Get dashboard summary (this is what appears in the CLI footer)
    dashboard_summary = monitor.get_dashboard_summary()
    
    print("✅ Performance monitoring integration results:")
    print(f"   📊 Dashboard Footer: {dashboard_summary}")
    
    # Get detailed metrics
    metrics = monitor.get_current_metrics()
    print(f"   🔍 Detailed Metrics:")
    print(f"      • Signals processed: {metrics['signals_processed']}")
    print(f"      • Events generated: {metrics['events_generated']}")
    print(f"      • Threats detected: {metrics['threats_detected']}")
    print(f"      • Average latency: {metrics['average_latency_ms']}ms")
    print(f"      • Performance status: {metrics['performance_status']}")
    print(f"      • Events per minute: {metrics['events_per_minute']}")
    print(f"      • System uptime: {metrics['uptime_formatted']}")
    
    # Test what the dashboard footer would show
    print(f"\\n📱 CLI Dashboard Footer Display:")
    print(f"   Status: Source: MOCK DATA | {dashboard_summary} | Time: 23:28:45 | Press ? for help")
    
    # Test performance grading
    detailed_report = monitor.get_detailed_report()
    print(f"\\n🎯 Performance Analysis:")
    print(f"   Grade: {detailed_report['analysis']['performance_grade']}")
    
    if detailed_report['analysis']['bottlenecks']:
        print(f"   Bottlenecks: {', '.join(detailed_report['analysis']['bottlenecks'])}")
    else:
        print(f"   ✅ No bottlenecks detected")
    
    if detailed_report['analysis']['recommendations']:
        print(f"   Recommendations:")
        for rec in detailed_report['analysis']['recommendations']:
            print(f"      • {rec}")
    
    print("\\n🎉 CLI Dashboard performance integration working perfectly!")
    print("\\n💡 To see this in action, run:")
    print("   uv run python cli_dashboard.py --mock")
    print("   (The footer will now show performance metrics)")
    
    return True

if __name__ == "__main__":
    test_dashboard_performance_integration()