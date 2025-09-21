#!/usr/bin/env python3
"""
Debug script for all JiraUtil commands.
This makes it easier to debug any command functionality.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the main function
from JiraUtil import main

def debug_command(command_args):
    """Debug a specific command with the given arguments."""
    print(f"Debugging command: {' '.join(command_args)}")
    print("-" * 50)
    
    # Set up the command line arguments
    sys.argv = command_args
    
    try:
        # Call the main function
        main()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("JiraUtil Debug Script")
    print("=" * 50)
    print()
    
    # Uncomment the command you want to debug:
    
    # CSV Commands
    # debug_command(["JiraUtil.py", "remove-newline", "test.csv"])
    # debug_command(["JiraUtil.py", "remove-newline", "test.csv", "--output", "test-clean.csv"])
    # debug_command(["JiraUtil.py", "extract-to-comma-separated-list", "Parent key", "test.csv"])
    # debug_command(["JiraUtil.py", "extract-to-comma-separated-list", "Assignee", "test.csv"])
    # debug_command(["JiraUtil.py", "fix-dates-eu", "test.csv"])
    # debug_command(["JiraUtil.py", "fix-dates-eu", "test.csv", "--output", "test-eu-dates.csv"])
    
    # Jira Commands
    # debug_command(["JiraUtil.py", "ResetTestFixture"])
    # debug_command(["JiraUtil.py", "ResetTestFixture", "rule-testing"])
    # debug_command(["JiraUtil.py", "ResetTestFixture", "my-custom-label"])
    # debug_command(["JiraUtil.py", "ResetTestFixture", "--jira-url", "https://company.atlassian.net", "--username", "user@company.com", "--password", "token"])
    
    # Help commands
    # debug_command(["JiraUtil.py", "--help"])
    # debug_command(["JiraUtil.py", "ResetTestFixture", "--help"])
    
    print("No command selected for debugging.")
    print("Uncomment one of the debug_command() calls above to debug a specific command.")
    print()
    print("Available commands to debug:")
    print("- CSV: remove-newline, extract-to-comma-separated-list, fix-dates-eu")
    print("- Jira: ResetTestFixture")
    print("- Help: --help")
