#!/usr/bin/env python3
"""
Debug script for JiraTest command.
This makes it easier to debug the JiraTest functionality.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the main function
from JiraCsv import main

if __name__ == "__main__":
    # Simulate command line arguments for JiraTest
    sys.argv = ["JiraCsv.py", "JiraTest"]
    
    # Call the main function
    main()
