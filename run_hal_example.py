#!/usr/bin/env python3
"""
Run the HAL example script.

This script ensures the hardware package is in the Python path before running the example.
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Now import and run the example
from backend.hardware.examples.hal_example import main

if __name__ == "__main__":
    main()
