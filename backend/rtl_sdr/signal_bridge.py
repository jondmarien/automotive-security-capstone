"""
signal_bridge.py

Performs real-time signal processing on IQ data from RTL-SDR to detect automotive security events.
Bridges the RTL-TCP server and Pico clients by analyzing IQ samples, detecting events, and broadcasting
detection results. Designed for use in the Automotive Security Capstone POC project.

Example usage:
    bridge = SignalProcessingBridge(rtl_server_manager)
    asyncio.run(bridge.start_signal_processing())
"""
import numpy as np
import asyncio
from datetime import datetime
import struct
from backend.detection.event_logic import analyze_event  # Unified detection/event logic

# TODO: Refactor this module for future Micropython compatibility (Pico deployment).

class SignalProcessingBridge:
    """
    Bridges RTL-TCP server and Pico clients by processing IQ samples from RTL-SDR, detecting automotive signals,
    and broadcasting detection events.

    Args:
        rtl_server_manager: Instance of RTLTCPServerManager for event broadcast.
        rtl_tcp_host (str): Host for RTL-TCP server (default 'localhost').
        rtl_tcp_port (int): Port for RTL-TCP server (default 1234).

    Example:
        bridge = SignalProcessingBridge(rtl_server_manager)
        asyncio.run(bridge.start_signal_processing())
    """
    def __init__(self, rtl_server_manager, rtl_tcp_host='localhost', rtl_tcp_port=1234):
        self.rtl_server = rtl_server_manager
        self.rtl_tcp_host = rtl_tcp_host
        self.rtl_tcp_port = rtl_tcp_port
        self.processing_active = False
        self.signal_buffer = []
        self.detection_threshold = -60

    async def start_signal_processing(self):
        """
        Main signal processing loop.
        Connects to RTL-TCP server, processes IQ samples, detects signals, and broadcasts results.

        Example:
            await bridge.start_signal_processing()
        """
        self.processing_active = True
        while self.processing_active:
            try:
                reader, writer = await asyncio.open_connection(
                    self.rtl_tcp_host, self.rtl_tcp_port
                )
                print("Connected to RTL-SDR V4 via TCP")
                await self.configure_rtl_sdr(writer)
                sample_count = 0
                while self.processing_active:
                    raw_data = await reader.read(16384)
                    if not raw_data:
                        print("No data from RTL-SDR, reconnecting...")
                        break
                    processed_data = await self.process_samples(raw_data, sample_count)
                    if processed_data:
                        await self.rtl_server.broadcast_to_picos(processed_data)
                    sample_count += 1
                    if sample_count % 100 == 0:
                        status = {
                            'type': 'status',
                            'samples_processed': sample_count,
                            'frequency': self.rtl_server.frequency,
                            'connected_picos': len(self.rtl_server.connected_picos)
                        }
                        await self.rtl_server.broadcast_to_picos(status)
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                print(f"Signal processing error: {e}")
                await asyncio.sleep(2)

    async def configure_rtl_sdr(self, writer):
        """
        Send configuration commands (frequency, sample rate, gain) to RTL-SDR over TCP.

        Args:
            writer: Asyncio StreamWriter for TCP connection.

        Example:
            await bridge.configure_rtl_sdr(writer)
        """
        freq_cmd = struct.pack('>BI', 0x01, self.rtl_server.frequency)
        writer.write(freq_cmd)
        rate_cmd = struct.pack('>BI', 0x02, self.rtl_server.sample_rate)
        writer.write(rate_cmd)
        gain_cmd = struct.pack('>BI', 0x04, self.rtl_server.gain)
        writer.write(gain_cmd)
        await writer.drain()
        print("RTL-SDR configured via TCP")

    async def process_samples(self, raw_data, sample_count):
        """
        Process IQ samples and detect signals.
        Converts raw IQ data to power spectrum, detects events, and returns detection dict.

        Args:
            raw_data (bytes): Raw IQ sample bytes from RTL-SDR.
            sample_count (int): Current sample batch number.

        Returns:
            dict or None: Detection event dict if signals detected, else None.

        Example:
            result = await bridge.process_samples(raw_data, 42)
        """
        samples = np.frombuffer(raw_data, dtype=np.uint8)
        i_samples = (samples[0::2].astype(np.float32) - 127.5) / 127.5
        q_samples = (samples[1::2].astype(np.float32) - 127.5) / 127.5
        min_len = min(len(i_samples), len(q_samples))
        i_samples = i_samples[:min_len]
        q_samples = q_samples[:min_len]
        complex_samples = i_samples + 1j * q_samples
        power_spectrum = np.abs(complex_samples) ** 2
        power_db = 10 * np.log10(power_spectrum + 1e-12)
        detections = await self.detect_automotive_signals(power_db, complex_samples)
        if detections:
            return {
                'type': 'signal_detection',
                'timestamp': datetime.now().isoformat(),
                'sample_count': sample_count,
                'detections': detections,
                'frequency_mhz': self.rtl_server.frequency / 1e6,
                'sample_rate': self.rtl_server.sample_rate
            }
        return None

    async def detect_automotive_signals(self, power_db, complex_samples):
        """
        Unified automotive signal detection logic using analyze_event().
        Converts SDR features into detection event(s) using unified logic.

        Args:
            power_db (np.ndarray): Power (dB) array from IQ samples.
            complex_samples (np.ndarray): Complex IQ samples.

        Returns:
            list: List of detection event dicts (empty if no detection).
        """
        detections = []
        mean_power = np.mean(power_db)
        std_power = np.std(power_db)
        threshold = mean_power + 3 * std_power
        peaks = np.where(power_db > threshold)[0]
        if len(peaks) > 0:
            max_power = np.max(power_db[peaks])
            burst_pattern = self.analyze_burst_pattern(power_db, peaks)
            # Build packet dict for unified logic
            packet = {
                "burst_pattern": burst_pattern,
                "max_power": float(max_power),
                "mean_power": float(mean_power),
                "peak_count": len(peaks),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "rssi": float(max_power),
                "freq": self.rtl_server.frequency / 1e6,
                # Feature flags for event_logic
                "is_replay": False,  # TODO: Add replay detection logic if available
                "is_jamming": burst_pattern == "jamming_pattern",
                "is_brute": False,   # TODO: Add brute force logic if available
                "is_unlock": burst_pattern == "key_fob_pattern",  # Simplified mapping
                "is_lock": False,    # TODO: Add lock logic if available
            }
            event = analyze_event(packet, demo_mode=False)
            detections.append(event)
        return detections

    def analyze_burst_pattern(self, power_db, peaks):
        """
        Analyze burst pattern in detected peaks to infer signal type.

        Args:
            power_db (np.ndarray): Power (dB) array.
            peaks (np.ndarray): Indices of detected peaks.

        Returns:
            str: Pattern label (e.g., 'key_fob_pattern', 'jamming_pattern', etc).
        """
        if len(peaks) < 3:
            return 'single_burst'
        peak_intervals = np.diff(peaks)
        if len(peak_intervals) >= 2:
            interval_consistency = np.std(peak_intervals) / np.mean(peak_intervals)
            if interval_consistency < 0.3:
                return 'key_fob_pattern'
        if len(peaks) > 10 and np.mean(peak_intervals) < 5:
            return 'jamming_pattern'
        return 'unknown_pattern'

    def classify_signal_type(self, burst_pattern, max_power):
        """
        Classify signal type based on burst pattern and power.

        Args:
            burst_pattern (str): Pattern label from analyze_burst_pattern.
            max_power (float): Maximum power in detected peaks.

        Returns:
            str: Signal type label (e.g., 'key_fob_transmission').
        """
        if burst_pattern == 'key_fob_pattern':
            return 'key_fob_transmission'
        elif burst_pattern == 'jamming_pattern':
            return 'potential_jamming'
        elif max_power > -50:
            return 'strong_unknown_signal'
        else:
            return 'weak_signal'

    def calculate_threat_level(self, burst_pattern, max_power, mean_power):
        """
        Calculate threat level based on burst pattern and power.

        Args:
            burst_pattern (str): Pattern label.
            max_power (float): Maximum detected power.
            mean_power (float): Mean power of the spectrum.

        Returns:
            float: Threat score (0.0 to 1.0).
        """
        threat_score = 0.0
        if burst_pattern == 'key_fob_pattern':
            threat_score += 0.6
        elif burst_pattern == 'jamming_pattern':
            threat_score += 0.9
        power_ratio = (max_power - mean_power) / abs(mean_power)
        threat_score += min(0.4, power_ratio / 10)
        return min(1.0, threat_score)