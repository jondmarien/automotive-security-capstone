"""
brute_force_detector.py

Enhanced brute force attack detector with temporal analysis and escalating threat levels.

This module provides the BruteForceDetector class which:
- Performs temporal analysis for detecting rapid signal attempts
- Implements pattern recognition for brute force attack signatures
- Provides escalating threat levels for repeated attempts
- Collects comprehensive evidence for technical proof of brute force attacks

The detector analyzes signal transmission patterns across multiple time windows
to identify suspicious, moderate, high, and critical threat levels based on
signal frequency, timing patterns, and consistency analysis.

Example usage:
    detector = BruteForceDetector(signal_history_buffer)
    result = detector.check_brute_force(detected_signal)
    if result['is_brute_force']:
        print(f"Brute force detected: {result['evidence']['attack_classification']['threat_level']}")
"""

import time
import numpy as np
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .signal_history_buffer import SignalHistoryBuffer
from .automotive_signal_analyzer import DetectedSignal

logger = logging.getLogger(__name__)

class BruteForceDetector:
    """
    Enhanced detector for brute force attacks with temporal analysis and escalating threat levels.
    
    This detector identifies rapid repeated attempts to access automotive systems by analyzing:
    - Signal transmission rates and patterns
    - Temporal clustering of similar signals
    - Escalating threat levels based on attempt frequency
    - Evidence collection for technical proof of brute force attacks
    """
    
    def __init__(self, signal_history: SignalHistoryBuffer):
        """Initialize enhanced brute force detector."""
        self.signal_history = signal_history
        
        # Multi-tier rate thresholds for escalating threat levels
        self.rate_thresholds = {
            'suspicious': 5,    # signals per minute - suspicious activity
            'moderate': 10,     # signals per minute - moderate threat
            'high': 20,         # signals per minute - high threat
            'critical': 40      # signals per minute - critical threat
        }
        
        # Time windows for different analysis types
        self.time_windows = {
            'short': 30,    # 30 seconds - rapid burst detection
            'medium': 60,   # 1 minute - standard brute force window
            'long': 300     # 5 minutes - sustained attack detection
        }
        
        # Pattern recognition parameters
        self.min_signals_for_pattern = 3
        self.rapid_burst_threshold = 2.0  # seconds between signals for rapid burst
        self.sustained_attack_duration = 120  # seconds for sustained attack classification
        
        logger.info("Enhanced BruteForceDetector initialized with multi-tier thresholds")
        
    def check_brute_force(self, detected_signal: DetectedSignal) -> Dict[str, Any]:
        """
        Enhanced brute force detection with temporal analysis and escalating threat levels.
        
        Args:
            detected_signal: Signal detected by AutomotiveSignalAnalyzer
            
        Returns:
            Brute force analysis results with escalating threat levels
        """
        # Perform temporal analysis across multiple time windows
        temporal_analysis = self._perform_temporal_analysis(detected_signal)
        
        # Analyze attack patterns
        pattern_analysis = self._analyze_attack_patterns(detected_signal, temporal_analysis)
        
        # Calculate escalating threat level
        threat_level = self._calculate_escalating_threat_level(temporal_analysis, pattern_analysis)
        
        # Determine if this constitutes a brute force attack
        is_brute_force = threat_level['level'] != 'benign'
        
        if is_brute_force:
            # Collect comprehensive evidence
            evidence = self._collect_brute_force_evidence(
                detected_signal, temporal_analysis, pattern_analysis, threat_level
            )
            
            logger.info(f"Brute force attack detected: {threat_level['level']} "
                       f"(confidence: {threat_level['confidence']:.2f})")
            
            return {
                'is_brute_force': True,
                'confidence': threat_level['confidence'],
                'evidence': evidence
            }
        
        return {'is_brute_force': False}
    
    def _perform_temporal_analysis(self, detected_signal: DetectedSignal) -> Dict[str, Any]:
        """
        Perform comprehensive temporal analysis for detecting rapid signal attempts.
        
        Args:
            detected_signal: Current signal being analyzed
            
        Returns:
            Temporal analysis results across multiple time windows
        """
        analysis = {}
        
        for window_name, window_duration in self.time_windows.items():
            # Get recent signals of the same type within this time window
            recent_signals = self.signal_history.get_signals_by_type(
                detected_signal.signal_type, 
                window_duration
            )
            
            signal_count = len(recent_signals)
            signal_rate = signal_count / (window_duration / 60)  # signals per minute
            
            # Calculate inter-signal intervals for this window
            intervals = self._calculate_inter_signal_intervals(recent_signals)
            
            analysis[window_name] = {
                'signal_count': signal_count,
                'signal_rate': signal_rate,
                'time_window': window_duration,
                'intervals': intervals,
                'rapid_bursts': self._detect_rapid_bursts(intervals),
                'sustained_activity': signal_count > 0 and window_duration >= self.sustained_attack_duration
            }
        
        logger.debug(f"Temporal analysis completed for {detected_signal.signal_type}: "
                    f"short={analysis['short']['signal_count']}, "
                    f"medium={analysis['medium']['signal_count']}, "
                    f"long={analysis['long']['signal_count']}")
        
        return analysis
    
    def _analyze_attack_patterns(self, detected_signal: DetectedSignal, temporal_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze signal patterns for brute force attack signatures.
        
        Args:
            detected_signal: Current signal being analyzed
            temporal_analysis: Results from temporal analysis
            
        Returns:
            Pattern analysis results
        """
        pattern_analysis = {
            'attack_type': 'unknown',
            'pattern_confidence': 0.0,
            'characteristics': {}
        }
        
        # Analyze short-term patterns (rapid bursts)
        short_term = temporal_analysis['short']
        if short_term['rapid_bursts']['count'] > 0:
            pattern_analysis['attack_type'] = 'rapid_burst'
            pattern_analysis['pattern_confidence'] = min(1.0, short_term['rapid_bursts']['count'] / 5.0)
            pattern_analysis['characteristics']['burst_pattern'] = short_term['rapid_bursts']
        
        # Analyze medium-term patterns (standard brute force)
        medium_term = temporal_analysis['medium']
        if medium_term['signal_rate'] > self.rate_thresholds['suspicious']:
            if pattern_analysis['attack_type'] == 'unknown':
                pattern_analysis['attack_type'] = 'sustained_brute_force'
            pattern_analysis['pattern_confidence'] = max(
                pattern_analysis['pattern_confidence'],
                min(1.0, medium_term['signal_rate'] / self.rate_thresholds['critical'])
            )
            pattern_analysis['characteristics']['sustained_rate'] = medium_term['signal_rate']
        
        # Analyze long-term patterns (persistent attacks)
        long_term = temporal_analysis['long']
        if long_term['sustained_activity'] and long_term['signal_count'] > 10:
            pattern_analysis['characteristics']['persistent_attack'] = True
            pattern_analysis['pattern_confidence'] = max(
                pattern_analysis['pattern_confidence'], 0.8
            )
        
        # Analyze signal consistency (identical repeated attempts)
        consistency_analysis = self._analyze_signal_consistency(detected_signal)
        pattern_analysis['characteristics']['signal_consistency'] = consistency_analysis
        
        return pattern_analysis
    
    def _calculate_escalating_threat_level(self, temporal_analysis: Dict[str, Any], 
                                         pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate escalating threat levels based on attempt frequency and patterns.
        
        Args:
            temporal_analysis: Temporal analysis results
            pattern_analysis: Pattern analysis results
            
        Returns:
            Threat level classification with confidence
        """
        # Start with medium-term analysis as baseline
        medium_term = temporal_analysis['medium']
        signal_rate = medium_term['signal_rate']
        
        # Determine base threat level from signal rate
        if signal_rate >= self.rate_thresholds['critical']:
            base_level = 'critical'
            base_confidence = 0.9
        elif signal_rate >= self.rate_thresholds['high']:
            base_level = 'high'
            base_confidence = 0.8
        elif signal_rate >= self.rate_thresholds['moderate']:
            base_level = 'moderate'
            base_confidence = 0.7
        elif signal_rate >= self.rate_thresholds['suspicious']:
            base_level = 'suspicious'
            base_confidence = 0.6
        else:
            base_level = 'benign'
            base_confidence = 0.0
        
        # For rates just above suspicious threshold, don't escalate unless pattern confidence is very high
        if base_level == 'suspicious' and signal_rate <= self.rate_thresholds['moderate']:
            # Only escalate if pattern confidence is extremely high
            if pattern_analysis['pattern_confidence'] > 0.95:
                base_level = 'moderate'
        
        # Escalate based on pattern analysis (but be more conservative)
        pattern_confidence = pattern_analysis['pattern_confidence']
        if pattern_confidence > 0.95:  # Increased threshold for escalation
            # High confidence patterns escalate threat level
            if base_level == 'suspicious':
                base_level = 'moderate'
            elif base_level == 'moderate':
                base_level = 'high'
            elif base_level == 'high':
                base_level = 'critical'
        
        # Escalate based on rapid bursts (but be more conservative)
        short_term = temporal_analysis['short']
        if short_term['rapid_bursts']['count'] > 10:  # Increased threshold for escalation
            base_confidence = min(1.0, base_confidence + 0.2)
            if base_level == 'suspicious':
                base_level = 'moderate'
        
        # Escalate based on sustained activity
        long_term = temporal_analysis['long']
        if long_term['sustained_activity'] and long_term['signal_count'] > 50:  # Increased threshold
            base_confidence = min(1.0, base_confidence + 0.1)
        
        return {
            'level': base_level,
            'confidence': base_confidence,
            'escalation_factors': {
                'signal_rate': signal_rate,
                'pattern_confidence': pattern_confidence,
                'rapid_bursts': short_term['rapid_bursts']['count'],
                'sustained_activity': long_term['sustained_activity']
            }
        }
    
    def _collect_brute_force_evidence(self, detected_signal: DetectedSignal, 
                                    temporal_analysis: Dict[str, Any],
                                    pattern_analysis: Dict[str, Any],
                                    threat_level: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect comprehensive evidence for technical proof of brute force attacks.
        
        Args:
            detected_signal: Current signal being analyzed
            temporal_analysis: Temporal analysis results
            pattern_analysis: Pattern analysis results
            threat_level: Calculated threat level
            
        Returns:
            Comprehensive evidence dictionary
        """
        evidence = {
            'attack_classification': {
                'threat_level': threat_level['level'],
                'confidence': threat_level['confidence'],
                'attack_type': pattern_analysis['attack_type']
            },
            'temporal_evidence': {},
            'pattern_evidence': pattern_analysis['characteristics'],
            'signal_evidence': {
                'signal_type': detected_signal.signal_type,
                'frequency': detected_signal.features.frequency,
                'timestamp': detected_signal.timestamp,
                'signal_strength': detected_signal.features.rssi
            },
            'statistical_analysis': {},
            'recommended_actions': self._generate_recommended_actions(threat_level['level']),
            'signal_rate': temporal_analysis['medium']['signal_rate']  # Added for test compatibility
        }
        
        # Collect temporal evidence for each time window
        for window_name, analysis in temporal_analysis.items():
            evidence['temporal_evidence'][window_name] = {
                'signal_count': analysis['signal_count'],
                'signal_rate_per_minute': analysis['signal_rate'],
                'time_window_seconds': analysis['time_window'],
                'rapid_burst_count': analysis['rapid_bursts']['count'],
                'average_interval': analysis['intervals']['average'] if analysis['intervals']['count'] > 0 else 0,
                'minimum_interval': analysis['intervals']['minimum'] if analysis['intervals']['count'] > 0 else 0
            }
        
        # Statistical analysis
        medium_intervals = temporal_analysis['medium']['intervals']
        if medium_intervals['count'] > 0:
            evidence['statistical_analysis'] = {
                'total_attempts': medium_intervals['count'] + 1,  # +1 for current signal
                'average_interval_seconds': medium_intervals['average'],
                'interval_standard_deviation': medium_intervals['std_dev'],
                'interval_consistency_score': self._calculate_interval_consistency(medium_intervals),
                'attack_duration_seconds': temporal_analysis['medium']['time_window'],
                'peak_rate_per_minute': max(
                    temporal_analysis['short']['signal_rate'],
                    temporal_analysis['medium']['signal_rate']
                )
            }
        
        return evidence
    
    def _calculate_inter_signal_intervals(self, signals: List) -> Dict[str, Any]:
        """Calculate inter-signal intervals with statistical analysis."""
        if len(signals) < 2:
            return {'count': 0, 'intervals': [], 'average': 0, 'minimum': 0, 'maximum': 0, 'std_dev': 0}
        
        # Extract timestamps and sort
        timestamps = [signal.timestamp for signal in signals]
        timestamps.sort()
        
        # Calculate intervals
        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        
        return {
            'count': len(intervals),
            'intervals': intervals,
            'average': np.mean(intervals),
            'minimum': np.min(intervals),
            'maximum': np.max(intervals),
            'std_dev': np.std(intervals)
        }
    
    def _detect_rapid_bursts(self, intervals: Dict[str, Any]) -> Dict[str, Any]:
        """Detect rapid burst patterns in signal intervals."""
        if intervals['count'] == 0:
            return {'count': 0, 'burst_intervals': [], 'average_burst_interval': 0}
        
        # Find intervals shorter than rapid burst threshold
        rapid_intervals = [interval for interval in intervals['intervals'] 
                          if interval <= self.rapid_burst_threshold]
        
        return {
            'count': len(rapid_intervals),
            'burst_intervals': rapid_intervals,
            'average_burst_interval': np.mean(rapid_intervals) if rapid_intervals else 0,
            'burst_percentage': len(rapid_intervals) / intervals['count'] if intervals['count'] > 0 else 0
        }
    
    def _analyze_signal_consistency(self, detected_signal: DetectedSignal) -> Dict[str, Any]:
        """Analyze consistency of repeated signals (identical attempts)."""
        # Get recent signals of the same type
        recent_signals = self.signal_history.get_signals_by_type(
            detected_signal.signal_type, 
            self.time_windows['medium']
        )
        
        if len(recent_signals) < 2:
            return {'consistency_score': 0.0, 'identical_signals': 0}
        
        # Compare current signal with recent signals
        identical_count = 0
        similarity_scores = []
        
        for historical_signal in recent_signals[-5:]:  # Check last 5 signals
            similarity = self._calculate_signal_similarity(detected_signal, historical_signal)
            similarity_scores.append(similarity)
            
            if similarity > 0.95:  # Very high similarity indicates identical attempts
                identical_count += 1
        
        consistency_score = np.mean(similarity_scores) if similarity_scores else 0.0
        
        return {
            'consistency_score': consistency_score,
            'identical_signals': identical_count,
            'similarity_scores': similarity_scores,
            'high_similarity_threshold': 0.95
        }
    
    def _calculate_signal_similarity(self, signal1: 'DetectedSignal', signal2: 'DetectedSignal') -> float:
        """
        Calculate similarity between two signals based on multiple features.
        
        Args:
            signal1: First detected signal
            signal2: Second detected signal
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        try:
            # Compare frequencies
            freq2 = getattr(signal2.features, 'frequency', 0)
            freq1 = getattr(signal1.features, 'frequency', 0)
            if freq1 != 0:
                freq_diff = abs(freq1 - freq2) / freq1
                # Make frequency differences more impactful
                freq_similarity = max(0, 1.0 - freq_diff * 5)  # Multiply by 5 to make it more sensitive
            else:
                freq_similarity = 0.0
            
            # Compare signal strength
            rssi1 = getattr(signal1.features, 'rssi', 0)
            rssi2 = getattr(signal2.features, 'rssi', 0)
            rssi_diff = abs(rssi1 - rssi2)
            # Make RSSI differences more impactful
            rssi_similarity = max(0, 1.0 - rssi_diff / 15.0)  # 15 dB range - more sensitive
            
            # Compare burst timing patterns
            timing1 = getattr(signal1.features, 'burst_timing', [])
            timing2 = getattr(signal2.features, 'burst_timing', [])
            timing_similarity = self._compare_burst_timing(timing1, timing2)
            
            # Weighted average - make it more sensitive to differences
            result = 0.6 * freq_similarity + 0.25 * rssi_similarity + 0.15 * timing_similarity
            
            # Debug logging for tests
            if hasattr(signal2, 'features') and hasattr(signal2.features, '__dict__'):
                logger.debug(f"Signal similarity debug - freq1: {freq1}, freq2: {freq2}, freq_similarity: {freq_similarity}")
                logger.debug(f"Signal similarity debug - rssi1: {rssi1}, rssi2: {rssi2}, rssi_similarity: {rssi_similarity}")
                logger.debug(f"Signal similarity debug - timing1: {timing1}, timing2: {timing2}, timing_similarity: {timing_similarity}")
                logger.debug(f"Signal similarity debug - result: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating signal similarity: {e}")
            return 0.0
    
    def _compare_burst_timing(self, timing1: List[float], timing2: List[float]) -> float:
        """Compare burst timing patterns between signals."""
        if len(timing1) != len(timing2) or len(timing1) == 0:
            return 0.0
        
        # Calculate timing differences
        timing_diffs = [abs(t1 - t2) for t1, t2 in zip(timing1, timing2)]
        avg_diff = np.mean(timing_diffs)
        
        # Convert to similarity score (smaller differences = higher similarity)
        return max(0, 1 - avg_diff / 0.01)  # 10ms threshold
    
    def _calculate_interval_consistency(self, intervals: Dict[str, Any]) -> float:
        """Calculate consistency score for signal intervals."""
        if intervals['count'] < 2 or intervals['average'] == 0:
            return 0.0
        
        # Coefficient of variation (std_dev / mean)
        cv = intervals['std_dev'] / intervals['average']
        
        # Convert to consistency score (lower CV = higher consistency)
        return max(0, 1 - cv)
    
    def _generate_recommended_actions(self, threat_level: str) -> List[str]:
        """Generate recommended actions based on threat level."""
        actions = {
            'suspicious': [
                'Monitor signal source for escalation',
                'Log all attempts for pattern analysis',
                'Consider implementing rate limiting'
            ],
            'moderate': [
                'Implement immediate rate limiting',
                'Alert security personnel',
                'Block signal source if possible',
                'Increase monitoring sensitivity'
            ],
            'high': [
                'Immediately block signal source',
                'Alert security team urgently',
                'Implement emergency protocols',
                'Consider frequency hopping if available',
                'Document attack for forensic analysis'
            ],
            'critical': [
                'EMERGENCY: Implement all countermeasures',
                'Isolate affected systems immediately',
                'Contact law enforcement if appropriate',
                'Switch to backup communication channels',
                'Initiate incident response procedures',
                'Preserve all evidence for investigation'
            ]
        }
        
        return actions.get(threat_level, ['Monitor and analyze'])
    
    def get_detector_stats(self) -> Dict[str, Any]:
        """Get detector statistics and configuration."""
        return {
            'rate_thresholds': self.rate_thresholds,
            'time_windows': self.time_windows,
            'rapid_burst_threshold': self.rapid_burst_threshold,
            'sustained_attack_duration': self.sustained_attack_duration,
            'min_signals_for_pattern': self.min_signals_for_pattern
        }