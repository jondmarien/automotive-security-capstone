"""
enhanced_signal_bridge.py

Enhanced signal processing bridge with real-time IQ analysis and automotive signal detection.
Integrates AutomotiveSignalAnalyzer for sophisticated signal processing and threat detection.

This module provides the EnhancedSignalProcessingBridge class which:
- Processes real-time IQ samples from RTL-SDR
- Uses AutomotiveSignalAnalyzer for advanced signal analysis
- Maintains signal history for replay detection
- Integrates with existing RTL-TCP server and event broadcasting
- Provides enhanced threat detection capabilities

Example usage:
    bridge = EnhancedSignalProcessingBridge(rtl_server_manager)
    asyncio.run(bridge.start_signal_processing())
"""

import numpy as np
import asyncio
from datetime import datetime
import struct
import time
import logging
from typing import Dict, List, Any, Optional

from .automotive_signal_analyzer import AutomotiveSignalAnalyzer, SignalFeatures, DetectedSignal
from .signal_history_buffer import SignalHistoryBuffer
from .brute_force_detector import BruteForceDetector

from detection.event_logic import analyze_event
from detection.threat_levels import ThreatLevel

logger = logging.getLogger(__name__)

def log(msg):
    """Logging function for compatibility with existing code."""
    logger.info(msg)

class ThreatDetectionEngine:
    """
    Enhanced threat detection engine for automotive signals.
    
    This class implements sophisticated threat detection algorithms including
    replay attack detection, jamming detection, and brute force detection.
    """
    
    def __init__(self, signal_history: SignalHistoryBuffer):
        """
        Initialize the threat detection engine.
        
        Args:
            signal_history: Signal history buffer for temporal analysis
        """
        self.signal_history = signal_history
        self.replay_detector = ReplayAttackDetector(signal_history)
        self.jamming_detector = JammingDetector()
        self.brute_force_detector = BruteForceDetector(signal_history)
        
        logger.info("ThreatDetectionEngine initialized")
    
    def analyze_threat(self, detected_signal: DetectedSignal) -> Dict[str, Any]:
        """
        Analyze a detected signal for security threats.
        
        Args:
            detected_signal: Signal detected by AutomotiveSignalAnalyzer
            
        Returns:
            Threat analysis results
        """
        threat_indicators = []
        
        # Replay attack detection
        replay_result = self.replay_detector.check_replay(detected_signal)
        if replay_result['is_replay']:
            threat_indicators.append({
                'type': 'replay_attack',
                'confidence': replay_result['confidence'],
                'evidence': replay_result['evidence']
            })
        
        # Jamming detection
        jamming_result = self.jamming_detector.check_jamming(detected_signal)
        if jamming_result['is_jamming']:
            threat_indicators.append({
                'type': 'jamming_attack',
                'confidence': jamming_result['confidence'],
                'evidence': jamming_result['evidence']
            })
        
        # Brute force detection
        brute_force_result = self.brute_force_detector.check_brute_force(detected_signal)
        if brute_force_result['is_brute_force']:
            threat_indicators.append({
                'type': 'brute_force_attack',
                'confidence': brute_force_result['confidence'],
                'evidence': brute_force_result['evidence']
            })
        
        # Generate threat event
        if threat_indicators:
            return self._generate_threat_event(detected_signal, threat_indicators)
        else:
            return self._generate_benign_event(detected_signal)
    
    def _generate_threat_event(self, detected_signal: DetectedSignal, threat_indicators: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a threat event from detected indicators."""
        # Use the highest confidence threat as primary
        primary_threat = max(threat_indicators, key=lambda x: x['confidence'])
        
        return {
            'detection_id': f"threat_{int(time.time())}_{id(detected_signal)}",
            'event_type': primary_threat['type'],
            'threat_level': self._calculate_threat_level(threat_indicators),
            'confidence': primary_threat['confidence'],
            'signal_type': detected_signal.signal_type,
            'timestamp': detected_signal.timestamp,
            'features': detected_signal.features.to_dict(),
            'threat_indicators': threat_indicators,
            'evidence': primary_threat['evidence'],
            'recommended_action': self._get_recommended_action(primary_threat['type'])
        }
    
    def _generate_benign_event(self, detected_signal: DetectedSignal) -> Dict[str, Any]:
        """Generate a benign event for legitimate signals."""
        return {
            'detection_id': f"benign_{int(time.time())}_{id(detected_signal)}",
            'event_type': f"{detected_signal.signal_type}_transmission",
            'threat_level': 0.0,  # Benign
            'confidence': detected_signal.confidence,
            'signal_type': detected_signal.signal_type,
            'timestamp': detected_signal.timestamp,
            'features': detected_signal.features.to_dict(),
            'threat_indicators': [],
            'evidence': {},
            'recommended_action': 'Monitor'
        }
    
    def _calculate_threat_level(self, threat_indicators: List[Dict[str, Any]]) -> float:
        """Calculate overall threat level from indicators."""
        if not threat_indicators:
            return 0.0
        
        # Weight different threat types
        threat_weights = {
            'replay_attack': 0.9,
            'jamming_attack': 0.8,
            'brute_force_attack': 0.7
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for indicator in threat_indicators:
            threat_type = indicator['type']
            confidence = indicator['confidence']
            weight = threat_weights.get(threat_type, 0.5)
            
            weighted_score += confidence * weight
            total_weight += weight
        
        if total_weight > 0:
            return min(1.0, weighted_score / total_weight)
        else:
            return 0.0
    
    def _get_recommended_action(self, threat_type: str) -> str:
        """Get recommended action for threat type."""
        actions = {
            'replay_attack': 'Block signal, investigate source',
            'jamming_attack': 'Locate jammer, switch frequency',
            'brute_force_attack': 'Implement rate limiting, monitor source'
        }
        return actions.get(threat_type, 'Monitor and analyze')

class ReplayAttackDetector:
    """Detector for replay attacks using signal similarity analysis."""
    
    def __init__(self, signal_history: SignalHistoryBuffer):
        """Initialize replay attack detector."""
        self.signal_history = signal_history
        self.similarity_threshold = 0.95
        self.time_window = 300  # 5 minutes
        
    def check_replay(self, detected_signal: DetectedSignal) -> Dict[str, Any]:
        """Check if signal is a replay attack."""
        # Convert detected signal to format for similarity comparison
        signal_data = {
            'signal_type': detected_signal.signal_type,
            'features': detected_signal.features.to_dict(),
            'timestamp': detected_signal.timestamp
        }
        
        # Find similar signals in history
        similar_signals = self.signal_history.find_similar_signals(
            signal_data, 
            self.similarity_threshold, 
            self.time_window
        )
        
        if similar_signals:
            # Check for replay characteristics
            for similar_signal in similar_signals:
                time_diff = detected_signal.timestamp - similar_signal.timestamp
                
                # Replay attacks typically have identical signals with different timing
                if self._has_replay_timing_characteristics(detected_signal, similar_signal, time_diff):
                    return {
                        'is_replay': True,
                        'confidence': self._calculate_replay_confidence(detected_signal, similar_signal),
                        'evidence': {
                            'original_timestamp': similar_signal.timestamp,
                            'replay_timestamp': detected_signal.timestamp,
                            'time_difference': time_diff,
                            'signal_similarity': self._calculate_similarity(detected_signal, similar_signal),
                            'timing_anomaly': self._analyze_timing_anomaly(detected_signal, similar_signal)
                        }
                    }
        
        return {'is_replay': False}
    
    def _has_replay_timing_characteristics(self, current_signal: DetectedSignal, 
                                         historical_signal, time_diff: float) -> bool:
        """Check if timing characteristics indicate replay attack."""
        # Replay attacks typically occur within minutes of original
        if time_diff < 1.0 or time_diff > 300.0:  # 1 second to 5 minutes
            return False
        
        # Check for identical burst patterns (strong replay indicator)
        current_timing = current_signal.features.burst_timing
        historical_timing = historical_signal.features.get('burst_timing', [])
        
        if len(current_timing) == len(historical_timing) and len(current_timing) > 0:
            # Calculate timing pattern similarity
            timing_diffs = [abs(c - h) for c, h in zip(current_timing, historical_timing)]
            avg_diff = np.mean(timing_diffs) if timing_diffs else 0
            
            # Very similar timing patterns indicate replay
            return avg_diff < 0.001  # Less than 1ms difference
        
        return False
    
    def _calculate_replay_confidence(self, current_signal: DetectedSignal, historical_signal) -> float:
        """Calculate confidence that this is a replay attack."""
        confidence = 0.0
        
        # Signal similarity contributes 60%
        similarity = self._calculate_similarity(current_signal, historical_signal)
        confidence += similarity * 0.6
        
        # Timing pattern match contributes 30%
        timing_match = self._calculate_timing_match(current_signal, historical_signal)
        confidence += timing_match * 0.3
        
        # Frequency characteristics match contributes 10%
        freq_match = self._calculate_frequency_match(current_signal, historical_signal)
        confidence += freq_match * 0.1
        
        return min(1.0, confidence)
    
    def _calculate_similarity(self, current_signal: DetectedSignal, historical_signal) -> float:
        """Calculate overall signal similarity."""
        # Use the signal history buffer's similarity calculation
        current_data = {
            'features': current_signal.features.to_dict(),
            'signal_type': current_signal.signal_type
        }
        
        return self.signal_history._calculate_signal_similarity(current_data, historical_signal.signal_data)
    
    def _calculate_timing_match(self, current_signal: DetectedSignal, historical_signal) -> float:
        """Calculate timing pattern match score."""
        current_timing = current_signal.features.burst_timing
        historical_timing = historical_signal.features.get('burst_timing', [])
        
        if len(current_timing) != len(historical_timing) or len(current_timing) == 0:
            return 0.0
        
        timing_diffs = [abs(c - h) for c, h in zip(current_timing, historical_timing)]
        avg_diff = np.mean(timing_diffs)
        
        # Convert to similarity score (smaller differences = higher similarity)
        return max(0, 1 - avg_diff / 0.005)  # 5ms threshold
    
    def _calculate_frequency_match(self, current_signal: DetectedSignal, historical_signal) -> float:
        """Calculate frequency characteristics match score."""
        current_freq_dev = current_signal.features.frequency_deviation
        historical_freq_dev = historical_signal.features.get('frequency_deviation', 0)
        
        if current_freq_dev == 0 and historical_freq_dev == 0:
            return 1.0
        
        max_dev = max(abs(current_freq_dev), abs(historical_freq_dev))
        if max_dev == 0:
            return 1.0
        
        diff = abs(current_freq_dev - historical_freq_dev)
        return max(0, 1 - diff / max_dev)
    
    def _analyze_timing_anomaly(self, current_signal: DetectedSignal, historical_signal) -> Dict[str, Any]:
        """Analyze timing anomalies that indicate replay."""
        return {
            'burst_count_match': len(current_signal.features.burst_timing) == len(historical_signal.features.get('burst_timing', [])),
            'inter_burst_similarity': self._calculate_timing_match(current_signal, historical_signal),
            'temporal_separation': current_signal.timestamp - historical_signal.timestamp
        }

class JammingDetector:
    """Detector for RF jamming attacks."""
    
    def __init__(self):
        """Initialize jamming detector."""
        self.noise_floor_threshold = -80  # dBm
        self.bandwidth_threshold = 100e3  # 100 kHz
        
    def check_jamming(self, detected_signal: DetectedSignal) -> Dict[str, Any]:
        """Check if signal indicates jamming attack."""
        features = detected_signal.features
        
        # Check for jamming indicators
        is_jamming = False
        confidence = 0.0
        evidence = {}
        
        # Wide bandwidth signal (potential broadband jamming)
        if features.signal_bandwidth > self.bandwidth_threshold:
            is_jamming = True
            confidence += 0.4
            evidence['broadband_interference'] = True
            evidence['bandwidth'] = features.signal_bandwidth
        
        # High noise floor
        if features.rssi > self.noise_floor_threshold:
            confidence += 0.3
            evidence['elevated_noise_floor'] = True
            evidence['rssi'] = features.rssi
        
        # Continuous signal (no burst pattern)
        if len(features.burst_timing) == 0 or len(features.burst_timing) > 20:
            confidence += 0.2
            evidence['continuous_transmission'] = True
            evidence['burst_count'] = len(features.burst_timing)
        
        # Low modulation complexity (noise-like)
        if features.modulation_type == 'Unknown':
            confidence += 0.1
            evidence['unrecognized_modulation'] = True
        
        return {
            'is_jamming': is_jamming and confidence > 0.5,
            'confidence': min(1.0, confidence),
            'evidence': evidence
        }


class EnhancedSignalProcessingBridge:
    """
    Enhanced signal processing bridge with advanced automotive signal analysis.
    
    This class integrates the AutomotiveSignalAnalyzer with the existing RTL-SDR
    infrastructure to provide sophisticated signal processing and threat detection.
    """
    
    def __init__(self, rtl_server_manager, rtl_tcp_host='localhost', rtl_tcp_port=1234):
        """
        Initialize the enhanced signal processing bridge.
        
        Args:
            rtl_server_manager: RTL server manager instance
            rtl_tcp_host: RTL-TCP server host
            rtl_tcp_port: RTL-TCP server port
        """
        self.rtl_server = rtl_server_manager
        self.rtl_tcp_host = rtl_tcp_host
        self.rtl_tcp_port = rtl_tcp_port
        self.processing_active = False
        
        # Initialize components
        self.signal_analyzer = AutomotiveSignalAnalyzer(sample_rate=rtl_server_manager.sample_rate)
        self.signal_history = SignalHistoryBuffer(max_size=1000, time_window=300)
        self.threat_detector = ThreatDetectionEngine(self.signal_history)
        
        # Performance tracking
        self.samples_processed = 0
        self.events_generated = 0
        self.last_status_time = time.time()
        
        logger.info(f"EnhancedSignalProcessingBridge initialized: host={rtl_tcp_host}, port={rtl_tcp_port}")
    
    async def start_signal_processing(self):
        """
        Main enhanced signal processing loop.
        
        Connects to RTL-TCP server, processes IQ samples using AutomotiveSignalAnalyzer,
        detects threats, and broadcasts results.
        """
        self.processing_active = True
        
        while self.processing_active:
            try:
                reader, writer = await asyncio.open_connection(
                    self.rtl_tcp_host, self.rtl_tcp_port
                )
                log("Connected to RTL-SDR V4 via TCP (Enhanced Bridge)")
                
                await self._configure_rtl_sdr(writer)
                
                sample_count = 0
                while self.processing_active:
                    raw_data = await reader.read(16384)
                    if not raw_data:
                        log("No data from RTL-SDR, reconnecting...")
                        break
                    
                    # Only process if at least one Pico is connected
                    if len(self.rtl_server.connected_picos) > 0:
                        processed_events = await self.process_samples(raw_data, sample_count)
                        
                        if processed_events:
                            for event in processed_events:
                                await self.rtl_server.broadcast_to_picos(event)
                                self.events_generated += 1
                    
                    sample_count += 1
                    self.samples_processed += 1
                    
                    # Send status updates
                    if sample_count % 100 == 0:
                        await self._send_status_update(sample_count)
                
                writer.close()
                await writer.wait_closed()
                
            except Exception as e:
                log(f"Enhanced signal processing error: {e}")
                await asyncio.sleep(2)
    
    async def _configure_rtl_sdr(self, writer):
        """Configure RTL-SDR via TCP commands."""
        freq_cmd = struct.pack('>BI', 0x01, self.rtl_server.frequency)
        writer.write(freq_cmd)
        
        rate_cmd = struct.pack('>BI', 0x02, self.rtl_server.sample_rate)
        writer.write(rate_cmd)
        
        gain_cmd = struct.pack('>BI', 0x04, self.rtl_server.gain)
        writer.write(gain_cmd)
        
        await writer.drain()
        log("RTL-SDR configured via TCP (Enhanced)")
    
    async def process_samples(self, raw_data: bytes, sample_count: int) -> List[Dict[str, Any]]:
        """
        Process IQ samples using enhanced automotive signal analysis.
        
        Args:
            raw_data: Raw IQ sample bytes from RTL-SDR
            sample_count: Current sample batch number
            
        Returns:
            List of detection events
        """
        try:
            # Convert raw IQ data to complex samples
            complex_samples = self._convert_iq_samples(raw_data)
            
            if len(complex_samples) == 0:
                return []
            
            # Extract signal features using AutomotiveSignalAnalyzer
            features = self.signal_analyzer.extract_features(complex_samples)
            features.frequency = self.rtl_server.frequency  # Set tuned frequency
            
            # Detect automotive signal patterns
            detected_signals = self.signal_analyzer.detect_automotive_patterns(features)
            
            events = []
            for detected_signal in detected_signals:
                # Analyze for threats
                threat_analysis = self.threat_detector.analyze_threat(detected_signal)
                
                # Add signal to history
                self.signal_history.add_signal(threat_analysis)
                
                # Convert to event format for broadcasting
                event = self._create_event_from_analysis(threat_analysis, sample_count)
                events.append(event)
                
                # Log significant detections
                if threat_analysis['threat_level'] > 0.5:
                    log(f"[THREAT] {threat_analysis['event_type']} detected: "
                        f"confidence={threat_analysis['confidence']:.2f}, "
                        f"threat_level={threat_analysis['threat_level']:.2f}")
            
            return events
            
        except Exception as e:
            logger.error(f"Error processing samples: {e}")
            return []
    
    def _convert_iq_samples(self, raw_data: bytes) -> np.ndarray:
        """Convert raw IQ bytes to complex samples."""
        try:
            samples = np.frombuffer(raw_data, dtype=np.uint8)
            
            # Separate I and Q samples
            i_samples = (samples[0::2].astype(np.float32) - 127.5) / 127.5
            q_samples = (samples[1::2].astype(np.float32) - 127.5) / 127.5
            
            # Ensure equal length
            min_len = min(len(i_samples), len(q_samples))
            i_samples = i_samples[:min_len]
            q_samples = q_samples[:min_len]
            
            # Create complex samples
            complex_samples = i_samples + 1j * q_samples
            
            return complex_samples
            
        except Exception as e:
            logger.error(f"Error converting IQ samples: {e}")
            return np.array([], dtype=complex)
    
    def _create_event_from_analysis(self, threat_analysis: Dict[str, Any], sample_count: int) -> Dict[str, Any]:
        """Create event dictionary from threat analysis."""
        return {
            'type': 'signal_detection',
            'timestamp': datetime.now().isoformat(),
            'sample_count': sample_count,
            'detections': [threat_analysis],
            'frequency_mhz': self.rtl_server.frequency / 1e6,
            'sample_rate': self.rtl_server.sample_rate,
            'enhanced_analysis': True
        }
    
    async def _send_status_update(self, sample_count: int):
        """Send status update to connected Picos."""
        current_time = time.time()
        time_elapsed = current_time - self.last_status_time
        
        if time_elapsed > 0:
            processing_rate = 100 / time_elapsed  # samples per second
            
            status = {
                'type': 'enhanced_status',
                'samples_processed': self.samples_processed,
                'events_generated': self.events_generated,
                'processing_rate': processing_rate,
                'frequency': self.rtl_server.frequency,
                'connected_picos': len(self.rtl_server.connected_picos),
                'buffer_stats': self.signal_history.get_buffer_stats(),
                'analyzer_stats': {
                    'sample_rate': self.signal_analyzer.sample_rate,
                    'detection_thresholds': self.signal_analyzer.detection_thresholds
                }
            }
            
            await self.rtl_server.broadcast_to_picos(status)
            self.last_status_time = current_time
    
    def stop_processing(self):
        """Stop the signal processing loop."""
        self.processing_active = False
        log("Enhanced signal processing stopped")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            'samples_processed': self.samples_processed,
            'events_generated': self.events_generated,
            'processing_active': self.processing_active,
            'buffer_stats': self.signal_history.get_buffer_stats(),
            'analyzer_config': {
                'sample_rate': self.signal_analyzer.sample_rate,
                'frequency_bands': self.signal_analyzer.frequency_bands,
                'detection_thresholds': self.signal_analyzer.detection_thresholds
            }
        }