import socket
import numpy as np
import asyncio
import json
from datetime import datetime
import struct

class SignalProcessingBridge:
    def __init__(self, rtl_server_manager, rtl_tcp_host='localhost', rtl_tcp_port=1234):
        self.rtl_server = rtl_server_manager
        self.rtl_tcp_host = rtl_tcp_host
        self.rtl_tcp_port = rtl_tcp_port
        self.processing_active = False
        self.signal_buffer = []
        self.detection_threshold = -60

    async def start_signal_processing(self):
        """Main signal processing loop"""
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
        """Send configuration commands to RTL-SDR"""
        freq_cmd = struct.pack('>BI', 0x01, self.rtl_server.frequency)
        writer.write(freq_cmd)
        rate_cmd = struct.pack('>BI', 0x02, self.rtl_server.sample_rate)
        writer.write(rate_cmd)
        gain_cmd = struct.pack('>BI', 0x04, self.rtl_server.gain)
        writer.write(gain_cmd)
        await writer.drain()
        print("RTL-SDR configured via TCP")

    async def process_samples(self, raw_data, sample_count):
        """Process IQ samples and detect signals"""
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
        """Automotive-specific signal detection logic"""
        detections = []
        mean_power = np.mean(power_db)
        std_power = np.std(power_db)
        threshold = mean_power + 3 * std_power
        peaks = np.where(power_db > threshold)[0]
        if len(peaks) > 0:
            max_power = np.max(power_db[peaks])
            burst_pattern = self.analyze_burst_pattern(power_db, peaks)
            detection = {
                'detection_id': f"det_{int(datetime.now().timestamp())}",
                'signal_type': self.classify_signal_type(burst_pattern, max_power),
                'power_db': float(max_power),
                'power_above_noise': float(max_power - mean_power),
                'peak_count': len(peaks),
                'burst_pattern': burst_pattern,
                'threat_level': self.calculate_threat_level(burst_pattern, max_power, mean_power)
            }
            detections.append(detection)
        return detections

    def analyze_burst_pattern(self, power_db, peaks):
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
        if burst_pattern == 'key_fob_pattern':
            return 'key_fob_transmission'
        elif burst_pattern == 'jamming_pattern':
            return 'potential_jamming'
        elif max_power > -50:
            return 'strong_unknown_signal'
        else:
            return 'weak_signal'

    def calculate_threat_level(self, burst_pattern, max_power, mean_power):
        threat_score = 0.0
        if burst_pattern == 'key_fob_pattern':
            threat_score += 0.6
        elif burst_pattern == 'jamming_pattern':
            threat_score += 0.9
        power_ratio = (max_power - mean_power) / abs(mean_power)
        threat_score += min(0.4, power_ratio / 10)
        return min(1.0, threat_score) 