#!/usr/bin/env python3
"""
Real Hardware Test Script

Quick test script to verify RTL-SDR V4 and Pico 2 W hardware detection
and basic functionality before running the full system.

Usage:
    python test_real_hardware.py [--verbose]
"""

import asyncio
import argparse
import logging
import sys
from hardware import RTLSDRInterface, PicoConnectionManager, HardwareManager

def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

async def test_rtl_sdr():
    """Test RTL-SDR hardware detection and configuration."""
    print("🔍 Testing RTL-SDR V4 Hardware...")
    print("-" * 40)
    
    rtl_sdr = RTLSDRInterface()
    
    # Test hardware detection
    print("1. Hardware Detection:")
    detected = rtl_sdr.detect_hardware()
    print(f"   Result: {'✅ DETECTED' if detected else '❌ NOT DETECTED'}")
    
    if detected:
        caps = rtl_sdr.get_capabilities()
        if caps:
            print(f"   Device: {caps.device_name}")
            print(f"   Tuner: {caps.tuner_type}")
            print(f"   Frequency Range: {caps.frequency_range[0]/1e6:.1f} - {caps.frequency_range[1]/1e6:.1f} MHz")
            print(f"   Automotive Support: {'✅ YES' if caps.supports_automotive_frequencies() else '❌ NO'}")
        
        # Test configuration
        print("\n2. Automotive Configuration:")
        configured = rtl_sdr.configure_for_automotive('key_fob_eu')
        print(f"   Result: {'✅ CONFIGURED' if configured else '❌ FAILED'}")
        
        if configured:
            config = rtl_sdr.get_configuration()
            print(f"   Frequency: {config['frequency']/1e6:.3f} MHz")
            print(f"   Sample Rate: {config['sample_rate']/1e6:.3f} MS/s")
            print(f"   Gain: {config['gain']}")
    
    else:
        print("   ℹ️  No RTL-SDR hardware detected")
        print("   💡 System will use mock mode for demonstration")
    
    print()
    return detected

async def test_pico_manager():
    """Test Pico W connection management."""
    print("📱 Testing Pico W Connection Management...")
    print("-" * 40)
    
    pico_manager = PicoConnectionManager()
    
    # Start server
    print("1. Starting TCP Server:")
    server_started = await pico_manager.start_server()
    print(f"   Result: {'✅ STARTED' if server_started else '❌ FAILED'}")
    
    if server_started:
        print(f"   Listening on: {pico_manager.server_host}:{pico_manager.server_port}")
        
        # Wait briefly for connections
        print("\n2. Checking for Pico W Connections:")
        print("   Waiting 10 seconds for connections...")
        
        for i in range(10):
            health = await pico_manager.check_health()
            connected = health['connected_devices']
            
            if connected > 0:
                print(f"   ✅ {connected} Pico W device(s) connected!")
                devices = pico_manager.get_connected_devices()
                for device_id in devices:
                    print(f"      - {device_id}")
                break
            
            await asyncio.sleep(1)
        else:
            print("   ⏳ No Pico W devices connected yet")
            print("   💡 Make sure your Pico W is programmed and connected to WiFi")
        
        # Stop server
        await pico_manager.stop_server()
    
    print()
    return server_started

async def test_hardware_manager():
    """Test complete hardware management system."""
    print("🎛️  Testing Hardware Management System...")
    print("-" * 40)
    
    manager = HardwareManager(enable_auto_recovery=True)
    
    # Initialize system
    print("1. System Initialization:")
    success = await manager.initialize(mock_mode=False)
    print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    if success:
        print(f"   System Status: {manager.system_status.value}")
        print(f"   Hardware Ready: {'✅ YES' if manager.is_hardware_ready() else '❌ NO'}")
        print(f"   Mock Mode: {'🎭 YES' if manager.is_mock_mode() else '🔧 NO'}")
        
        # Get health status
        print("\n2. Health Status:")
        health = manager.get_health_status()
        print(f"   RTL-SDR: {health.rtl_sdr_status.value}")
        print(f"   Pico W: {health.pico_connections}/{health.total_pico_devices} connected")
        print(f"   Uptime: {health.uptime:.1f} seconds")
        
        # Start monitoring briefly
        print("\n3. Monitoring Test:")
        await manager.start_monitoring()
        print("   ✅ Monitoring started")
        
        # Wait a bit
        await asyncio.sleep(3)
        
        # Stop monitoring
        await manager.stop_monitoring()
        print("   ✅ Monitoring stopped")
    
    print()
    return success

async def run_comprehensive_test():
    """Run comprehensive hardware test."""
    print("🚀 Automotive Security Hardware Test")
    print("=" * 50)
    print()
    
    results = {}
    
    # Test RTL-SDR
    results['rtl_sdr'] = await test_rtl_sdr()
    
    # Test Pico Manager
    results['pico_manager'] = await test_pico_manager()
    
    # Test Hardware Manager
    results['hardware_manager'] = await test_hardware_manager()
    
    # Summary
    print("📊 Test Summary")
    print("-" * 20)
    print(f"RTL-SDR Hardware: {'✅ PASS' if results['rtl_sdr'] else '❌ FAIL (Mock Available)'}")
    print(f"Pico W Manager: {'✅ PASS' if results['pico_manager'] else '❌ FAIL'}")
    print(f"Hardware Manager: {'✅ PASS' if results['hardware_manager'] else '❌ FAIL'}")
    
    overall_success = all(results.values())
    print(f"\nOverall Result: {'✅ ALL SYSTEMS GO!' if overall_success else '⚠️  PARTIAL SUCCESS'}")
    
    if not overall_success:
        print("\n💡 Recommendations:")
        if not results['rtl_sdr']:
            print("   - Check RTL-SDR USB connection and drivers")
            print("   - System can run in mock mode for demonstration")
        if not results['pico_manager']:
            print("   - Verify Pico W is programmed and on network")
            print("   - Check firewall settings for port 8888")
        if not results['hardware_manager']:
            print("   - Check system logs for detailed error information")
    
    print("\n🎯 Next Steps:")
    if overall_success:
        print("   Ready to run: python real_hardware_launcher.py")
    else:
        print("   For demo: python real_hardware_launcher.py --force-mock")
    print("   Dashboard: python cli_dashboard.py --source tcp")
    
    return overall_success

async def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description="Test real hardware components")
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    try:
        success = await run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())