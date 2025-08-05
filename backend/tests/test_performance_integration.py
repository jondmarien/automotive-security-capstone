#!/usr/bin/env python3
"""
Quick test of performance monitoring integration
"""

from utils.simple_performance_monitor import get_performance_monitor


def test_performance_monitoring():
    """Test the performance monitoring system."""
    print("🧪 Testing Performance Monitoring Integration")
    print("=" * 50)

    # Get the performance monitor
    monitor = get_performance_monitor()

    # Simulate some activity
    print("📊 Recording test data...")
    monitor.record_signal_processed(45.0)  # Good latency
    monitor.record_signal_processed(65.0)  # Still good
    monitor.record_signal_processed(120.0)  # Fair latency

    # Record different event types
    monitor.record_event_generated("key_fob_transmission")
    monitor.record_event_generated("replay_attack")
    monitor.record_event_generated("jamming_attack")

    # Update system health
    monitor.update_system_health(
        rtl_sdr_connected=True, pico_w_connected=True, memory_usage_mb=89.5
    )

    # Get metrics
    metrics = monitor.get_current_metrics()
    dashboard_summary = monitor.get_dashboard_summary()

    print("✅ Performance monitoring results:")
    print(f"   Signals processed: {metrics['signals_processed']}")
    print(f"   Events generated: {metrics['events_generated']}")
    print(f"   Threats detected: {metrics['threats_detected']}")
    print(f"   Average latency: {metrics['average_latency_ms']}ms")
    print(f"   Performance status: {metrics['performance_status']}")
    print(f"   RTL-SDR status: {metrics['rtl_sdr_status']}")
    print(f"   Pico W status: {metrics['pico_w_status']}")
    print(f"   Memory usage: {metrics['memory_usage_mb']}MB")
    print()
    print(f"📋 Dashboard summary: {dashboard_summary}")

    # Test detailed report
    detailed_report = monitor.get_detailed_report()
    print(f"🎯 Performance grade: {detailed_report['analysis']['performance_grade']}")

    if detailed_report["analysis"]["bottlenecks"]:
        print("⚠️  Bottlenecks detected:")
        for bottleneck in detailed_report["analysis"]["bottlenecks"]:
            print(f"   • {bottleneck}")
    else:
        print("✅ No performance bottlenecks detected")

    print("\n🎉 Performance monitoring integration test completed successfully!")
    return True


if __name__ == "__main__":
    test_performance_monitoring()
