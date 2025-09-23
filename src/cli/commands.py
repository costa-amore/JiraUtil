"""
Command implementations for Jira utilities CLI.
"""

import sys
from pathlib import Path
from version import get_version
from config import get_config_file_status_message


def show_list() -> None:
    """Show available commands and their descriptions."""
    print("JiraUtil - Available Commands")
    print("=" * 40)
    print()
    print("CSV Export Commands:")
    print("  csv-export remove-newlines <input>     Remove newline characters from CSV fields")
    print("  csv-export extract-to-comma-separated-list <field> <input>  Extract field values")
    print("  csv-export fix-dates-eu <input>        Convert dates for European Excel")
    print()
    print("Test Fixture Commands:")
    print("  test-fixture reset [label]             Reset test fixture issues")
    print("  test-fixture assert [label]            Assert test fixture expectations")
    print()
    print("Utility Commands:")
    print("  list                                   Show this command list")
    print("  status                                 Show tool status")
    print("  --version, -v                          Show version")
    print("  --help, -h                             Show help")
    print()
    print("Short Aliases:")
    print("  ce rn <input>                          csv-export remove-newlines")
    print("  ce ecl <field> <input>                 csv-export extract-to-comma-separated-list")
    print("  ce fd <input>                          csv-export fix-dates-eu")
    print("  tf r [label]                           test-fixture reset")
    print("  tf a [label]                           test-fixture assert")
    print("  ls                                     list")
    print("  st                                     status")


def show_status() -> None:
    """Show tool status and information."""
    print("JiraUtil Status")
    print("=" * 20)
    print(f"Version: {get_version()}")
    print("Status: Ready")
    print()
    print("Configuration:")
    
    # Check if running as executable to determine context
    if getattr(sys, 'frozen', False):
        # Running as executable - user context
        config_file = "jira_config.env"
        config_path = Path(config_file)
        
        if config_path.exists():
            print(get_config_file_status_message(config_path))
        else:
            print(f"  Jira credentials: ❌ {config_file} not found - needs to be created")
        
        print("  Alternative: Set JIRA_URL, JIRA_USERNAME, JIRA_PASSWORD environment variables")
    else:
        # Running as script - development context
        venv_config = Path('.venv') / 'jira_config.env'
        local_config = Path('jira_config.env')
        
        config_file = None
        is_venv_config = False
        if venv_config.exists():
            config_file = venv_config
            is_venv_config = True
        elif local_config.exists():
            config_file = local_config
        
        if config_file:
            print(get_config_file_status_message(config_file, is_venv_config))
        else:
            print("  Jira credentials: No config file found - check .venv/jira_config.env or environment variables")
    
    print("  Default test fixture label: rule-testing")
    print()
    print("Available commands: Use 'JiraUtil list' or 'JiraUtil --help'")
