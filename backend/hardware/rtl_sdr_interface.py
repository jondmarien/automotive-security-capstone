"""
RTL-SDR Hardware Interface and Auto-Detection System

This module provides comprehensive RTL-SDR hardware detection, configuration,
and health monitoring capabilities for the automotive security monitoring system.

Features:
- Automatic RTL-SDR device detection using rtl_test integration
- Hardware capability detection and validation
- Automatic frequency and gain configuration for automotive bands
- Connection health monitoring and diagnostics
- Graceful fallback to mock mode for demonstrations

Example:
    interface = RTLSDRInterface()
    if interface.detect_hardware():
        capabilities = interface.get_capabilities()
        interface.configure_for_automotive()
"""

import subprocess
import logging
import time
import os
import re
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)

class RTLSDRStatus(Enum):
    """RTL-SDR hardware status enumeration."""
    NOT_DETECTED = "not_detected"
    DETECTED = "detected"
    CONFIGURED = "configured"
    CONNECTED = "connected"
    ERROR = "error"
    MOCK_MODE = "mock_mode"

@dataclass
class RTLSDRCapabilities:
    """RTL-SDR hardware capabilities and specifications."""
    device_index: int
    device_name: str
    tuner_type: str
    frequency_range: Tuple[int, int]  # (min_freq, max_freq) in Hz
    sample_rates: List[int]  # Supported sample rates in Hz
    gain_values: List[float]  # Supported gain values in dB
    usb_vendor_id: str
    usb_product_id: str
    serial_number: Optional[str] = None
    
    def supports_automotive_frequencies(self) -> bool:
        """Check if device supports automotive frequency bands."""
        automotive_bands = [
            (315000000, 315000000),  # 315 MHz (North America)
            (433920000, 433920000),  # 433.92 MHz (Europe)
            (868000000, 868000000),  # 868 MHz (Europe ISM)
        ]
        
        for freq_min, freq_max in automotive_bands:
            if self.frequency_range[0] <= freq_min <= self.frequency_range[1]:
                return True
        return False

class RTLSDRInterface:
    """
    RTL-SDR hardware interface with auto-detection and configuration.
    
    Provides comprehensive RTL-SDR hardware management including:
    - Automatic device detection and enumeration
    - Hardware capability assessment
    - Automotive-specific configuration
    - Health monitoring and diagnostics
    - Graceful fallback to mock mode
    """
    
    # Automotive frequency bands (Hz)
    AUTOMOTIVE_FREQUENCIES = {
        'key_fob_na': 315000000,      # 315 MHz - North American key fobs, TPMS
        'key_fob_eu': 433920000,      # 433.92 MHz - European key fobs, TPMS
        'ism_868': 868000000,         # 868 MHz - European ISM band
        'cellular_700': 700000000,    # 700 MHz - Cellular band
        'cellular_850': 850000000,    # 850 MHz - Cellular band
    }
    
    # Optimal sample rates for automotive monitoring
    AUTOMOTIVE_SAMPLE_RATES = [
        2048000,  # 2.048 MS/s - Standard for key fob monitoring
        1024000,  # 1.024 MS/s - Lower bandwidth applications
        250000,   # 250 kS/s - Narrow band monitoring
    ]
    
    def __init__(self, rtl_sdr_bin_path: Optional[str] = None):
        """
        Initialize RTL-SDR interface.
        
        Args:
            rtl_sdr_bin_path: Path to RTL-SDR binaries directory.
                            If None, uses default backend/rtl_sdr_bin/
        """
        self.status = RTLSDRStatus.NOT_DETECTED
        self.capabilities: Optional[RTLSDRCapabilities] = None
        self.current_config: Dict[str, Any] = {}
        self.health_stats: Dict[str, Any] = {}
        self.mock_mode = False
        
        # Set RTL-SDR binary paths
        if rtl_sdr_bin_path is None:
            # Default to backend/rtl_sdr_bin/ directory
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            rtl_sdr_bin_path = os.path.join(backend_dir, 'rtl_sdr_bin')
        
        self.rtl_sdr_bin_path = rtl_sdr_bin_path
        self.rtl_test_path = os.path.join(rtl_sdr_bin_path, 'rtl_test.exe')
        self.rtl_tcp_path = os.path.join(rtl_sdr_bin_path, 'rtl_tcp.exe')
        
        logger.info(f"RTL-SDR interface initialized with binary path: {rtl_sdr_bin_path}")
    
    def detect_hardware(self) -> bool:
        """
        Detect RTL-SDR hardware using rtl_test integration.
        
        Returns:
            bool: True if RTL-SDR hardware detected and functional, False otherwise.
        """
        logger.info("Starting RTL-SDR hardware detection...")
        
        try:
            # Check if rtl_test executable exists
            if not os.path.exists(self.rtl_test_path):
                logger.error(f"rtl_test not found at {self.rtl_test_path}")
                self.status = RTLSDRStatus.ERROR
                return False
            
            # Run rtl_test to detect hardware
            result = subprocess.run(
                [self.rtl_test_path, '-t'],  # -t for extended test
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.error(f"rtl_test failed with return code {result.returncode}")
                logger.error(f"stderr: {result.stderr}")
                
                # Check for common error messages
                if "No supported devices found" in result.stderr:
                    logger.error("No RTL-SDR devices found - check USB connection and drivers")
                elif "usb_claim_interface error" in result.stderr:
                    logger.error("USB interface claim error - device may be in use")
                elif "Failed to open rtlsdr device" in result.stderr:
                    logger.error("Failed to open RTL-SDR device - check permissions")
                
                self.status = RTLSDRStatus.ERROR
                return False
            
            # Parse rtl_test output to extract capabilities
            self.capabilities = self._parse_rtl_test_output(result.stdout)
            
            if self.capabilities:
                logger.info(f"RTL-SDR detected: {self.capabilities.device_name}")
                logger.info(f"Tuner: {self.capabilities.tuner_type}")
                logger.info(f"Frequency range: {self.capabilities.frequency_range[0]/1e6:.1f} - {self.capabilities.frequency_range[1]/1e6:.1f} MHz")
                
                # Verify automotive frequency support
                if self.capabilities.supports_automotive_frequencies():
                    logger.info("Device supports automotive frequency bands")
                    self.status = RTLSDRStatus.DETECTED
                    return True
                else:
                    logger.warning("Device does not support automotive frequency bands")
                    self.status = RTLSDRStatus.ERROR
                    return False
            else:
                logger.error("Failed to parse RTL-SDR capabilities")
                self.status = RTLSDRStatus.ERROR
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("rtl_test timed out - device may be unresponsive")
            self.status = RTLSDRStatus.ERROR
            return False
        except FileNotFoundError:
            logger.error(f"rtl_test executable not found: {self.rtl_test_path}")
            self.status = RTLSDRStatus.ERROR
            return False
        except Exception as e:
            logger.error(f"Unexpected error during hardware detection: {e}")
            self.status = RTLSDRStatus.ERROR
            return False
    
    def _parse_rtl_test_output(self, output: str) -> Optional[RTLSDRCapabilities]:
        """
        Parse rtl_test output to extract device capabilities.
        
        Args:
            output: Raw output from rtl_test command
            
        Returns:
            RTLSDRCapabilities object or None if parsing failed
        """
        try:
            lines = output.strip().split('\n')
            
            # Initialize default values
            device_index = 0
            device_name = "Unknown RTL-SDR"
            tuner_type = "Unknown"
            frequency_range = (24000000, 1766000000)  # Default RTL-SDR range
            sample_rates = self.AUTOMOTIVE_SAMPLE_RATES.copy()
            gain_values = [0.0, 0.9, 1.4, 2.7, 3.7, 7.7, 8.7, 12.5, 14.4, 15.7, 16.6, 19.7, 20.7, 22.9, 25.4, 28.0, 29.7, 32.8, 33.8, 36.4, 37.2, 38.6, 40.2, 42.1, 43.4, 43.9, 44.5, 48.0, 49.6]
            usb_vendor_id = "0bda"
            usb_product_id = "2838"
            serial_number = None
            
            # Parse output lines
            for line in lines:
                line = line.strip()
                
                # Extract device name
                if "Found" in line and "RTL" in line:
                    # Example: "Found 1 device(s): 0: Realtek, RTL2838UHIDIR, SN: 00000001"
                    match = re.search(r':\s*(.+?)(?:,\s*SN:|$)', line)
                    if match:
                        device_name = match.group(1).strip()
                
                # Extract serial number
                if "SN:" in line:
                    match = re.search(r'SN:\s*(\w+)', line)
                    if match:
                        serial_number = match.group(1)
                
                # Extract tuner type
                if "Tuner:" in line:
                    match = re.search(r'Tuner:\s*(.+)', line)
                    if match:
                        tuner_type = match.group(1).strip()
                
                # Extract frequency range
                if "Tuner gain" in line or "supported gain" in line:
                    # Look for frequency range in surrounding lines
                    continue
            
            # Determine frequency range based on tuner type
            if "R820T" in tuner_type or "R828D" in tuner_type:
                frequency_range = (24000000, 1766000000)  # R820T/R828D range
            elif "E4000" in tuner_type:
                frequency_range = (52000000, 2200000000)  # E4000 range
            elif "FC0013" in tuner_type:
                frequency_range = (22000000, 1100000000)  # FC0013 range
            
            return RTLSDRCapabilities(
                device_index=device_index,
                device_name=device_name,
                tuner_type=tuner_type,
                frequency_range=frequency_range,
                sample_rates=sample_rates,
                gain_values=gain_values,
                usb_vendor_id=usb_vendor_id,
                usb_product_id=usb_product_id,
                serial_number=serial_number
            )
            
        except Exception as e:
            logger.error(f"Error parsing rtl_test output: {e}")
            return None
    
    def configure_for_automotive(self, frequency_band: str = 'key_fob_eu') -> bool:
        """
        Configure RTL-SDR for optimal automotive signal monitoring.
        
        Args:
            frequency_band: Automotive frequency band to monitor
                          ('key_fob_na', 'key_fob_eu', 'ism_868', etc.)
        
        Returns:
            bool: True if configuration successful, False otherwise
        """
        if self.status != RTLSDRStatus.DETECTED:
            logger.error("Cannot configure RTL-SDR - hardware not detected")
            return False
        
        if frequency_band not in self.AUTOMOTIVE_FREQUENCIES:
            logger.error(f"Unknown frequency band: {frequency_band}")
            return False
        
        frequency = self.AUTOMOTIVE_FREQUENCIES[frequency_band]
        
        # Verify frequency is supported
        if not (self.capabilities.frequency_range[0] <= frequency <= self.capabilities.frequency_range[1]):
            logger.error(f"Frequency {frequency/1e6:.1f} MHz not supported by device")
            return False
        
        # Select optimal sample rate
        sample_rate = 2048000  # Default to 2.048 MS/s for automotive
        for rate in self.AUTOMOTIVE_SAMPLE_RATES:
            if rate in self.capabilities.sample_rates:
                sample_rate = rate
                break
        
        # Select optimal gain (auto gain for now)
        gain = "auto"
        
        # Store configuration
        self.current_config = {
            'frequency': frequency,
            'frequency_band': frequency_band,
            'sample_rate': sample_rate,
            'gain': gain,
            'configured_at': time.time()
        }
        
        self.status = RTLSDRStatus.CONFIGURED
        
        logger.info(f"RTL-SDR configured for automotive monitoring:")
        logger.info(f"  Frequency: {frequency/1e6:.3f} MHz ({frequency_band})")
        logger.info(f"  Sample rate: {sample_rate/1e6:.3f} MS/s")
        logger.info(f"  Gain: {gain}")
        
        return True
    
    def get_capabilities(self) -> Optional[RTLSDRCapabilities]:
        """
        Get RTL-SDR hardware capabilities.
        
        Returns:
            RTLSDRCapabilities object or None if not detected
        """
        return self.capabilities
    
    def get_status(self) -> RTLSDRStatus:
        """Get current RTL-SDR status."""
        return self.status
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current RTL-SDR configuration."""
        return self.current_config.copy()
    
    def check_health(self) -> Dict[str, Any]:
        """
        Perform health check on RTL-SDR hardware.
        
        Returns:
            Dictionary containing health status and diagnostics
        """
        health_status = {
            'timestamp': time.time(),
            'status': self.status.value,
            'hardware_detected': self.status != RTLSDRStatus.NOT_DETECTED,
            'configuration_valid': bool(self.current_config),
            'mock_mode': self.mock_mode,
            'errors': []
        }
        
        # Check if hardware is still accessible
        if self.status in [RTLSDRStatus.DETECTED, RTLSDRStatus.CONFIGURED, RTLSDRStatus.CONNECTED]:
            try:
                # Quick hardware check
                result = subprocess.run(
                    [self.rtl_test_path, '-t'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode != 0:
                    health_status['errors'].append("Hardware no longer accessible")
                    health_status['hardware_detected'] = False
                    self.status = RTLSDRStatus.ERROR
                
            except Exception as e:
                health_status['errors'].append(f"Health check failed: {e}")
                health_status['hardware_detected'] = False
        
        # Update health stats
        self.health_stats = health_status
        
        return health_status
    
    def enable_mock_mode(self) -> None:
        """Enable mock mode for demonstrations without hardware."""
        logger.info("Enabling RTL-SDR mock mode")
        self.mock_mode = True
        self.status = RTLSDRStatus.MOCK_MODE
        
        # Create mock capabilities
        self.capabilities = RTLSDRCapabilities(
            device_index=0,
            device_name="Mock RTL-SDR V4",
            tuner_type="Mock R828D",
            frequency_range=(24000000, 1766000000),
            sample_rates=self.AUTOMOTIVE_SAMPLE_RATES,
            gain_values=[0.0, 9.7, 14.4, 27.8, 37.2, 77.6, 87.0, 125.0, 144.0, 157.0, 166.0, 197.0],
            usb_vendor_id="mock",
            usb_product_id="mock",
            serial_number="MOCK001"
        )
        
        # Set default automotive configuration
        self.current_config = {
            'frequency': self.AUTOMOTIVE_FREQUENCIES['key_fob_eu'],
            'frequency_band': 'key_fob_eu',
            'sample_rate': 2048000,
            'gain': 'auto',
            'configured_at': time.time()
        }
    
    def is_mock_mode(self) -> bool:
        """Check if interface is in mock mode."""
        return self.mock_mode
    
    def get_diagnostic_info(self) -> Dict[str, Any]:
        """
        Get comprehensive diagnostic information.
        
        Returns:
            Dictionary containing detailed diagnostic data
        """
        return {
            'status': self.status.value,
            'capabilities': self.capabilities.__dict__ if self.capabilities else None,
            'configuration': self.current_config,
            'health_stats': self.health_stats,
            'mock_mode': self.mock_mode,
            'binary_paths': {
                'rtl_test': self.rtl_test_path,
                'rtl_tcp': self.rtl_tcp_path,
                'bin_directory': self.rtl_sdr_bin_path
            },
            'automotive_frequencies': self.AUTOMOTIVE_FREQUENCIES,
            'supported_sample_rates': self.AUTOMOTIVE_SAMPLE_RATES
        }