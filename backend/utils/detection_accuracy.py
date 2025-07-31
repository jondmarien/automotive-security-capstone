"""
detection_accuracy.py

Provides tools for validating the accuracy of the detection system.
Includes confusion matrix generation, statistical analysis, and benchmark testing.
"""

import numpy as np
import logging
import time
import asyncio
from typing import Dict, List, Tuple, Any
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns

# Import signal constants
from utils.signal_constants import (
    ScenarioType,
    AttackType,
    ModulationType
)

# Import synthetic event generator for testing
from cli_dashboard_detection_adapter import (
    generate_synthetic_key_fob_event,
    generate_synthetic_replay_attack,
    generate_synthetic_jamming_attack,
    generate_synthetic_brute_force_attack,
    generate_synthetic_signal_cloning_attack,
    generate_synthetic_relay_attack
)

# Import detection logic
from detection.event_logic import analyze_event

class DetectionAccuracyValidator:
    """
    Validates the accuracy of the detection system using synthetic events.
    Generates confusion matrices, statistical analyses, and performance benchmarks.
    """
    
    def __init__(self):
        self.true_labels = []
        self.predicted_labels = []
        self.confidence_scores = []
        self.processing_times = []
        self.event_types = []
        
    async def generate_test_dataset(self, num_samples: int = 100) -> List[Dict]:
        """
        Generate a test dataset with known ground truth labels.
        
        Args:
            num_samples: Number of test samples to generate
            
        Returns:
            List of test events with ground truth labels
        """
        test_dataset = []
        
        # Define scenario distribution
        scenarios = [
            {"type": "benign", "weight": 0.5},
            {"type": "replay_attack", "weight": 0.1},
            {"type": "jamming_attack", "weight": 0.1},
            {"type": "brute_force_attack", "weight": 0.1},
            {"type": "signal_cloning_attack", "weight": 0.1},
            {"type": "relay_attack", "weight": 0.1}
        ]
        
        # Generate test events based on scenario distribution
        for _ in range(num_samples):
            # Choose scenario based on weights
            scenario_type = np.random.choice(
                [s["type"] for s in scenarios],
                p=[s["weight"] for s in scenarios]
            )
            
            # Generate appropriate event based on scenario
            if scenario_type == "benign":
                event = generate_synthetic_key_fob_event("benign")
                true_label = "benign"
            elif scenario_type == "replay_attack":
                # Create a benign event first to replay
                original_event = generate_synthetic_key_fob_event("benign")
                event = generate_synthetic_replay_attack(original_event)
                true_label = "replay_attack"
            elif scenario_type == "jamming_attack":
                # Random step in jamming sequence
                step = np.random.randint(0, 5)
                event = generate_synthetic_jamming_attack(step)
                true_label = "jamming_attack"
            elif scenario_type == "brute_force_attack":
                # Random step in brute force sequence
                step = np.random.randint(0, 5)
                event = generate_synthetic_brute_force_attack(step)
                true_label = "brute_force_attack"
            elif scenario_type == "signal_cloning_attack":
                # Random step in signal cloning sequence
                step = np.random.randint(0, 5)
                event = generate_synthetic_signal_cloning_attack(step)
                true_label = "signal_cloning_attack"
            elif scenario_type == "relay_attack":
                # Random step in relay attack sequence
                step = np.random.randint(0, 5)
                event = generate_synthetic_relay_attack(step)
                true_label = "relay_attack"
            
            # Add ground truth label
            event["true_label"] = true_label
            test_dataset.append(event)
            
            # Small delay to prevent system overload
            await asyncio.sleep(0.01)
            
        return test_dataset
    
    async def evaluate_detection_accuracy(self, num_samples: int = 100) -> Dict:
        """
        Evaluate the detection accuracy using synthetic events.
        
        Args:
            num_samples: Number of test samples to use
            
        Returns:
            Dictionary with accuracy metrics
        """
        logging.info(f"Starting detection accuracy validation with {num_samples} samples")
        
        # Generate test dataset
        test_dataset = await self.generate_test_dataset(num_samples)
        
        # Process each event and record results
        self.true_labels = []
        self.predicted_labels = []
        self.confidence_scores = []
        self.processing_times = []
        self.event_types = []
        
        for event in test_dataset:
            # Record true label
            true_label = event["true_label"]
            self.true_labels.append(true_label)
            
            # Process event through detection system
            start_time = time.time()
            enriched_event = analyze_event(event)
            end_time = time.time()
            
            # Record processing time
            processing_time = (end_time - start_time) * 1000  # Convert to ms
            self.processing_times.append(processing_time)
            
            # Extract predicted label
            if "threat" in enriched_event:
                if enriched_event["threat"] == "Malicious":
                    if "type" in enriched_event:
                        if "Replay" in enriched_event["type"]:
                            predicted_label = "replay_attack"
                        elif "Jamming" in enriched_event["type"]:
                            predicted_label = "jamming_attack"
                        elif "Brute Force" in enriched_event["type"]:
                            predicted_label = "brute_force_attack"
                        elif "Signal Cloning" in enriched_event["type"]:
                            predicted_label = "signal_cloning_attack"
                        elif "Relay" in enriched_event["type"]:
                            predicted_label = "relay_attack"
                        else:
                            predicted_label = "unknown_attack"
                    else:
                        predicted_label = "unknown_attack"
                else:
                    predicted_label = "benign"
            else:
                predicted_label = "unknown"
            
            self.predicted_labels.append(predicted_label)
            
            # Extract confidence score if available
            confidence = enriched_event.get("confidence", 0.0)
            self.confidence_scores.append(confidence)
            
            # Record event type
            event_type = enriched_event.get("type", "Unknown")
            self.event_types.append(event_type)
            
            # Small delay to prevent system overload
            await asyncio.sleep(0.01)
        
        # Calculate accuracy metrics
        accuracy_metrics = self.calculate_accuracy_metrics()
        
        # Generate confusion matrix
        self.generate_confusion_matrix()
        
        # Generate performance report
        performance_metrics = self.calculate_performance_metrics()
        
        # Combine all metrics
        results = {
            "accuracy_metrics": accuracy_metrics,
            "performance_metrics": performance_metrics
        }
        
        return results
    
    def calculate_accuracy_metrics(self) -> Dict:
        """
        Calculate accuracy metrics based on true and predicted labels.
        
        Returns:
            Dictionary with accuracy metrics
        """
        # Get unique labels
        unique_labels = list(set(self.true_labels + self.predicted_labels))
        
        # Calculate overall accuracy
        correct_predictions = sum(1 for true, pred in zip(self.true_labels, self.predicted_labels) if true == pred)
        total_predictions = len(self.true_labels)
        overall_accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        
        # Calculate per-class metrics
        class_metrics = {}
        for label in unique_labels:
            # True positives
            tp = sum(1 for true, pred in zip(self.true_labels, self.predicted_labels) 
                    if true == label and pred == label)
            
            # False positives
            fp = sum(1 for true, pred in zip(self.true_labels, self.predicted_labels) 
                    if true != label and pred == label)
            
            # False negatives
            fn = sum(1 for true, pred in zip(self.true_labels, self.predicted_labels) 
                    if true == label and pred != label)
            
            # Calculate precision, recall, and F1 score
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            class_metrics[label] = {
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "support": self.true_labels.count(label)
            }
        
        # Calculate average confidence score
        avg_confidence = sum(self.confidence_scores) / len(self.confidence_scores) if self.confidence_scores else 0
        
        return {
            "overall_accuracy": overall_accuracy,
            "class_metrics": class_metrics,
            "average_confidence": avg_confidence
        }
    
    def calculate_performance_metrics(self) -> Dict:
        """
        Calculate performance metrics based on processing times.
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.processing_times:
            return {
                "avg_processing_time_ms": 0,
                "min_processing_time_ms": 0,
                "max_processing_time_ms": 0,
                "processing_time_p95_ms": 0,
                "processing_time_p99_ms": 0,
                "real_time_requirement_met": False
            }
        
        # Calculate statistics
        avg_time = sum(self.processing_times) / len(self.processing_times)
        min_time = min(self.processing_times)
        max_time = max(self.processing_times)
        p95_time = np.percentile(self.processing_times, 95)
        p99_time = np.percentile(self.processing_times, 99)
        
        # Check if real-time requirement is met (< 500ms)
        real_time_requirement_met = p95_time < 500
        
        return {
            "avg_processing_time_ms": avg_time,
            "min_processing_time_ms": min_time,
            "max_processing_time_ms": max_time,
            "processing_time_p95_ms": p95_time,
            "processing_time_p99_ms": p99_time,
            "real_time_requirement_met": real_time_requirement_met
        }
    
    def generate_confusion_matrix(self, save_path: str = None) -> np.ndarray:
        """
        Generate and optionally save a confusion matrix visualization.
        
        Args:
            save_path: Path to save the confusion matrix image
            
        Returns:
            Confusion matrix as numpy array
        """
        # Get unique labels
        unique_labels = sorted(list(set(self.true_labels + self.predicted_labels)))
        
        # Generate confusion matrix
        cm = confusion_matrix(
            self.true_labels, 
            self.predicted_labels,
            labels=unique_labels
        )
        
        # Normalize confusion matrix
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        
        # Create visualization if save_path is provided
        if save_path:
            plt.figure(figsize=(10, 8))
            sns.heatmap(
                cm_normalized, 
                annot=True, 
                fmt='.2f', 
                xticklabels=unique_labels,
                yticklabels=unique_labels,
                cmap='Blues'
            )
            plt.xlabel('Predicted Label')
            plt.ylabel('True Label')
            plt.title('Normalized Confusion Matrix')
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close()
        
        return cm
    
    def generate_classification_report(self) -> str:
        """
        Generate a classification report using sklearn's classification_report.
        
        Returns:
            Classification report as string
        """
        return classification_report(
            self.true_labels,
            self.predicted_labels
        )
    
    def save_results_to_file(self, results: Dict, file_path: str) -> None:
        """
        Save validation results to a file.
        
        Args:
            results: Results dictionary
            file_path: Path to save results
        """
        with open(file_path, 'w') as f:
            # Write header
            f.write("# Detection Accuracy Validation Results\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Write accuracy metrics
            f.write("## Accuracy Metrics\n")
            accuracy_metrics = results["accuracy_metrics"]
            f.write(f"Overall Accuracy: {accuracy_metrics['overall_accuracy']:.2%}\n")
            f.write(f"Average Confidence Score: {accuracy_metrics['average_confidence']:.2f}\n\n")
            
            # Write class metrics
            f.write("### Class Metrics\n")
            f.write("| Class | Precision | Recall | F1 Score | Support |\n")
            f.write("|-------|-----------|--------|----------|--------|\n")
            
            for label, metrics in accuracy_metrics["class_metrics"].items():
                f.write(f"| {label} | {metrics['precision']:.2f} | {metrics['recall']:.2f} | ")
                f.write(f"{metrics['f1_score']:.2f} | {metrics['support']} |\n")
            
            f.write("\n")
            
            # Write performance metrics
            f.write("## Performance Metrics\n")
            perf_metrics = results["performance_metrics"]
            f.write(f"Average Processing Time: {perf_metrics['avg_processing_time_ms']:.2f} ms\n")
            f.write(f"Minimum Processing Time: {perf_metrics['min_processing_time_ms']:.2f} ms\n")
            f.write(f"Maximum Processing Time: {perf_metrics['max_processing_time_ms']:.2f} ms\n")
            f.write(f"95th Percentile Processing Time: {perf_metrics['processing_time_p95_ms']:.2f} ms\n")
            f.write(f"99th Percentile Processing Time: {perf_metrics['processing_time_p99_ms']:.2f} ms\n")
            f.write(f"Real-time Requirement Met: {'Yes' if perf_metrics['real_time_requirement_met'] else 'No'}\n")
            
            # Write classification report
            f.write("\n## Classification Report\n```\n")
            f.write(self.generate_classification_report())
            f.write("\n```\n")


async def run_accuracy_validation(num_samples: int = 100, output_dir: str = "results") -> None:
    """
    Run the detection accuracy validation and save results.
    
    Args:
        num_samples: Number of test samples to use
        output_dir: Directory to save results
    """
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize validator
    validator = DetectionAccuracyValidator()
    
    # Run validation
    results = await validator.evaluate_detection_accuracy(num_samples)
    
    # Save confusion matrix
    validator.generate_confusion_matrix(save_path=os.path.join(output_dir, "confusion_matrix.png"))
    
    # Save results to file
    validator.save_results_to_file(results, os.path.join(output_dir, "accuracy_results.md"))
    
    # Log summary
    accuracy = results["accuracy_metrics"]["overall_accuracy"]
    avg_time = results["performance_metrics"]["avg_processing_time_ms"]
    logging.info(f"Validation complete: Accuracy={accuracy:.2%}, Avg Processing Time={avg_time:.2f}ms")
    
    # Check if accuracy meets requirement (>90%)
    if accuracy >= 0.9:
        logging.info("[PASS] Accuracy requirement met (>90%)")
    else:
        logging.warning("[FAIL] Accuracy requirement not met (<90%)")
    
    # Check if real-time requirement is met
    if results["performance_metrics"]["real_time_requirement_met"]:
        logging.info("[PASS] Real-time processing requirement met (<500ms)")
    else:
        logging.warning("[FAIL] Real-time processing requirement not met (>500ms)")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run validation
    import asyncio
    asyncio.run(run_accuracy_validation())
