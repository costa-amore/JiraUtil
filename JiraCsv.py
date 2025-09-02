#!/usr/bin/env python3
"""
Entry point for JiraCsv CLI tool.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the main function directly from the module
from JiraCsv import main

if __name__ == "__main__":
	main()
