#!/usr/bin/env python3
"""
Short alias for JiraUtil.py
This file provides a convenient 'ju' command as an alternative to 'JiraUtil'.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import and run the main function from JiraUtil
from JiraUtil import main

if __name__ == "__main__":
    main()
