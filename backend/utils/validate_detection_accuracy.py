#!/usr/bin/env python
"""
validate_detection_accuracy.py

Script to run detection accuracy validation and generate reports.
This validates that the detection system meets the >90% accuracy requirement
and the real-time processing requirement (<500ms).
"""

import argparse
import asyncio
import logging
import os
from datetime import datetime
from utils.detection_accuracy import run_accuracy_validation


def setup_logging():
    """Set up logging configuration."""
    log_dir = os.path.join("logs")
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"accuracy_validation_{timestamp}.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run detection accuracy validation")
    parser.add_argument(
        "--samples",
        type=int,
        default=100,
        help="Number of test samples to use (default: 100)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results",
        help="Directory to save results (default: results)",
    )
    return parser.parse_args()


async def main():
    """Main entry point."""
    # Set up logging
    setup_logging()

    # Parse arguments
    args = parse_args()

    # Log start
    logging.info(f"Starting detection accuracy validation with {args.samples} samples")
    logging.info(f"Results will be saved to {args.output_dir}")

    # Create results directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(args.output_dir, f"validation_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Run validation
        await run_accuracy_validation(args.samples, output_dir)

        # Log completion
        logging.info(f"Validation complete. Results saved to {output_dir}")
        print(f"\nValidation complete! Results saved to {output_dir}")
        print("Check the accuracy_results.md file for detailed metrics.")

    except Exception as e:
        logging.exception(f"Error during validation: {e}")
        print(f"\nError during validation: {e}")


if __name__ == "__main__":
    asyncio.run(main())
