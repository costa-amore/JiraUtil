"""
Functional tests for CLI commands.

This module tests the complete CLI functionality including:
- list command
- status command
- version command
- help command
- Command parsing and routing
"""

import pytest
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from io import StringIO

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cli.parser import build_parser
from cli.commands import show_list, show_status
from version.manager import get_version
from config.validator import check_config_file_for_template_values, get_config_file_status_message


class TestCLIListCommand:
    """Test the list command functionality."""
    
    def test_list_command_displays_all_commands(self):
        """Test that list command displays all available commands."""
        with patch('builtins.print') as mock_print:
            show_list()
        
        # Verify all major command categories are displayed
        printed_content = ' '.join([str(call) for call in mock_print.call_args_list])
        
        assert "CSV Export Commands:" in printed_content
        assert "csv-export remove-newlines" in printed_content
        assert "csv-export extract-to-comma-separated-list" in printed_content
        assert "csv-export fix-dates-eu" in printed_content
        
        assert "Test Fixture Commands:" in printed_content
        assert "test-fixture reset" in printed_content
        assert "test-fixture assert" in printed_content
        
        assert "Utility Commands:" in printed_content
        assert "list" in printed_content
        assert "status" in printed_content
        assert "--version" in printed_content
        assert "--help" in printed_content
        
        assert "Short Aliases:" in printed_content
        assert "ce rn" in printed_content
        assert "ce ecl" in printed_content
        assert "ce fd" in printed_content
        assert "tf r" in printed_content
        assert "tf a" in printed_content
        assert "ls" in printed_content
        assert "st" in printed_content
    
    def test_list_command_formatting(self):
        """Test that list command has proper formatting."""
        with patch('builtins.print') as mock_print:
            show_list()
        
        # Check that we have the expected number of print calls (headers + commands)
        assert mock_print.call_count >= 20, "Should have multiple print statements for formatting"
        
        # Check for proper header formatting
        printed_content = [str(call) for call in mock_print.call_args_list]
        assert any("=" in line for line in printed_content), "Should have separator lines"
        assert any("JiraUtil - Available Commands" in line for line in printed_content), "Should have main header"


class TestCLIStatusCommand:
    """Test the status command functionality."""
    
    def test_status_command_displays_basic_info(self):
        """Test that status command displays basic tool information."""
        with patch('builtins.print') as mock_print, \
             patch('version.manager.get_version', return_value="1.0.24"):
            show_status()
        
        # Verify basic information is displayed
        printed_content = ' '.join([str(call) for call in mock_print.call_args_list])
        
        assert "JiraUtil Status" in printed_content
        assert "Version: 1.0.24" in printed_content
        assert "Status: Ready" in printed_content
        assert "Configuration:" in printed_content
        assert "Default test fixture label: rule-testing" in printed_content
    
    def test_status_command_displays_config_status_executable_mode(self):
        """Test status command in executable mode (no config file)."""
        with patch('builtins.print') as mock_print, \
             patch('version.manager.get_version', return_value="1.0.24"), \
             patch('version.manager.is_frozen', return_value=True), \
             patch('pathlib.Path.exists', return_value=False):
            show_status()
        
        printed_content = ' '.join([str(call) for call in mock_print.call_args_list])
        
        assert "jira_config.env not found" in printed_content
        assert "needs to be created" in printed_content
        assert "Set JIRA_URL, JIRA_USERNAME, JIRA_PASSWORD" in printed_content
    
    
    def test_status_command_displays_no_config_development_mode(self):
        """Test status command in development mode without config file."""
        with patch('builtins.print') as mock_print, \
             patch('version.manager.get_version', return_value="1.0.24"), \
             patch('version.manager.is_frozen', return_value=False), \
             patch('pathlib.Path.exists', return_value=False):
            show_status()
        
        printed_content = ' '.join([str(call) for call in mock_print.call_args_list])
        
        assert "No config file found" in printed_content
        assert ".venv/jira_config.env" in printed_content


class TestCLIVersionCommand:
    """Test the version command functionality."""
    
    
    def test_version_command_development_mode(self):
        """Test version command when running in development mode."""
        with patch('version.manager.is_frozen', return_value=False), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data='{"major": 1, "minor": 0, "build": 24}')):
            
            version = get_version()
            assert version == "1.0.24"
    
    def test_version_command_fallback(self):
        """Test version command fallback when version detection fails."""
        with patch('version.manager.is_frozen', return_value=False), \
             patch('pathlib.Path.exists', return_value=False):
            
            version = get_version()
            assert version == "unknown"


class TestCLICommandParsing:
    """Test CLI command parsing and routing."""
    
    def test_parser_creation(self):
        """Test that argument parser is created correctly."""
        parser = build_parser()
        
        assert parser.prog == "JiraUtil"
        assert parser.description == "Jira utilities"
        
        # Test that subcommands exist
        subcommands = [action.dest for action in parser._actions if hasattr(action, 'dest') and action.dest == 'command']
        assert 'command' in subcommands
    
    def test_csv_export_subcommands(self):
        """Test CSV export subcommand parsing."""
        parser = build_parser()
        
        # Test csv-export command
        args = parser.parse_args(['csv-export', 'remove-newlines', 'input.csv'])
        assert args.command == 'csv-export'
        assert args.csv_command == 'remove-newlines'
        assert args.input == 'input.csv'
        
        # Test csv-export with alias - the alias 'ce' maps to 'csv-export'
        args = parser.parse_args(['ce', 'rn', 'input.csv'])
        assert args.command == 'ce'  # The alias is preserved as the command
        assert args.csv_command == 'rn'  # The alias is preserved as the subcommand
        assert args.input == 'input.csv'
        
        # Test extract command
        args = parser.parse_args(['csv-export', 'extract-to-comma-separated-list', 'Status', 'input.csv'])
        assert args.command == 'csv-export'
        assert args.csv_command == 'extract-to-comma-separated-list'
        assert args.field_name == 'Status'
        assert args.input == 'input.csv'
        
        # Test fix-dates command
        args = parser.parse_args(['csv-export', 'fix-dates-eu', 'input.csv', '--output', 'output.csv'])
        assert args.command == 'csv-export'
        assert args.csv_command == 'fix-dates-eu'
        assert args.input == 'input.csv'
        assert args.output == 'output.csv'
    
    def test_testfixture_subcommands(self):
        """Test test fixture subcommand parsing."""
        parser = build_parser()
        
        # Test reset command
        args = parser.parse_args(['test-fixture', 'reset', 'custom-label'])
        assert args.command == 'test-fixture'
        assert args.test_command == 'reset'
        assert args.label == 'custom-label'
        
        # Test reset with alias - the alias 'tf' maps to 'test-fixture'
        args = parser.parse_args(['tf', 'r'])
        assert args.command == 'tf'  # The alias is preserved as the command
        assert args.test_command == 'r'  # The alias is preserved as the subcommand
        assert args.label == 'rule-testing'  # Default label
        
        # Test assert command
        args = parser.parse_args(['test-fixture', 'assert', 'custom-label'])
        assert args.command == 'test-fixture'
        assert args.test_command == 'assert'
        assert args.label == 'custom-label'
        
        # Test assert with alias
        args = parser.parse_args(['tf', 'a'])
        assert args.command == 'tf'  # The alias is preserved as the command
        assert args.test_command == 'a'  # The alias is preserved as the subcommand
        assert args.label == 'rule-testing'  # Default label
    
    def test_utility_commands(self):
        """Test utility command parsing."""
        parser = build_parser()
        
        # Test list command
        args = parser.parse_args(['list'])
        assert args.command == 'list'
        
        # Test list with alias - the alias 'ls' maps to 'list'
        args = parser.parse_args(['ls'])
        assert args.command == 'ls'  # The alias is preserved as the command
        
        # Test status command
        args = parser.parse_args(['status'])
        assert args.command == 'status'
        
        # Test status with alias
        args = parser.parse_args(['st'])
        assert args.command == 'st'  # The alias is preserved as the command
    
    def test_version_and_help_options(self):
        """Test version and help options."""
        parser = build_parser()
        
        # Test version option
        with pytest.raises(SystemExit):  # --version causes sys.exit
            parser.parse_args(['--version'])
        
        # Test help option
        with pytest.raises(SystemExit):  # --help causes sys.exit
            parser.parse_args(['--help'])


class TestConfigValidation:
    """Test configuration file validation functionality."""
    
    def test_check_config_file_template_values_detected(self):
        """Test detection of template values in config file."""
        config_content = """# Jira Configuration
JIRA_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=your.email@example.com
JIRA_PASSWORD=your_api_token_here
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as config_file:
            config_file.write(config_content)
            config_path = Path(config_file.name)
        
        try:
            has_template, message = check_config_file_for_template_values(config_path)
            
            assert has_template is True
            assert "template values" in message
            assert "needs configuration" in message
            
        finally:
            config_path.unlink(missing_ok=True)
    
    def test_check_config_file_no_template_values(self):
        """Test detection when no template values are present."""
        config_content = """# Jira Configuration
JIRA_URL=https://mycompany.atlassian.net
JIRA_USERNAME=john.doe@mycompany.com
JIRA_PASSWORD=abc123def456ghi789
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as config_file:
            config_file.write(config_content)
            config_path = Path(config_file.name)
        
        try:
            has_template, message = check_config_file_for_template_values(config_path)
            
            assert has_template is False
            assert "appears to be configured" in message
            
        finally:
            config_path.unlink(missing_ok=True)
    
    def test_get_config_file_status_message_template_values(self):
        """Test status message generation for template values."""
        config_path = Path("test_config.env")
        
        with patch('config.validator.check_config_file_for_template_values', return_value=(True, "Template detected")):
            message = get_config_file_status_message(config_path)
            
            assert "Jira credentials: Template detected" in message
    
    def test_get_config_file_status_message_configured(self):
        """Test status message generation for configured file."""
        config_path = Path("test_config.env")
        
        with patch('config.validator.check_config_file_for_template_values', return_value=(False, "Configured")):
            message = get_config_file_status_message(config_path, is_venv_config=True)
            
            assert "Jira credentials: Configured" in message


class TestCLIIntegration:
    """Test CLI integration and end-to-end functionality."""
    
    def test_main_help_integration(self):
        """Test that main help command works end-to-end."""
        from unittest.mock import patch
        import sys
        
        # Test the extracted run_cli function with help arguments
        with patch('sys.argv', ['JiraUtil.py', '--help']):
            with patch('builtins.print') as mock_print:
                from src.JiraUtil import run_cli
                
                # Help command causes argparse to call sys.exit(0), so we expect SystemExit
                try:
                    result = run_cli()
                    # If we get here, help wasn't processed correctly
                    assert False, "Expected SystemExit for help command"
                except SystemExit as e:
                    # SystemExit(0) is expected for help command
                    assert e.code == 0, f"Expected exit code 0, got {e.code}"
                    # Verify help was displayed (captured in stdout)
                    # The help output is captured by pytest, so we just verify the exception
    
    def test_main_list_integration(self):
        """Test that main list command works end-to-end."""
        from unittest.mock import patch
        import sys
        
        # Test the extracted run_cli function with list arguments
        with patch('sys.argv', ['JiraUtil.py', 'list']):
            with patch('builtins.print') as mock_print:
                from src.JiraUtil import run_cli
                result = run_cli()
                
                # Verify the result structure
                assert result['command'] == 'list'
                assert result['success'] == True
                
                # Verify list was displayed
                printed_content = ' '.join([str(call) for call in mock_print.call_args_list])
                assert "JiraUtil - Available Commands" in printed_content
    
    def test_main_status_integration(self):
        """Test that main status command works end-to-end."""
        from unittest.mock import patch
        import sys
        
        # Test the extracted run_cli function with status arguments
        with patch('sys.argv', ['JiraUtil.py', 'status']):
            with patch('builtins.print') as mock_print, \
                 patch('version.manager.get_version', return_value="1.0.24"), \
                 patch('version.manager.is_frozen', return_value=False), \
                 patch('pathlib.Path.exists', return_value=False):
                from src.JiraUtil import run_cli
                result = run_cli()
                
                # Verify the result structure
                assert result['command'] == 'status'
                assert result['success'] == True
                
                # Verify status was displayed
                printed_content = ' '.join([str(call) for call in mock_print.call_args_list])
                assert "JiraUtil Status" in printed_content
    
    def test_main_csv_export_integration(self):
        """Test that main CSV export commands work end-to-end."""
        from unittest.mock import patch
        import sys
        import tempfile
        import os
        
        # Create a temporary CSV file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_file.write("Name,Description\nTest,Line1\nLine2")
            temp_file_path = temp_file.name
        
        try:
            # Test the extracted run_cli function with CSV export arguments
            with patch('sys.argv', ['JiraUtil.py', 'csv-export', 'remove-newlines', temp_file_path]):
                with patch('builtins.print') as mock_print:
                    from src.JiraUtil import run_cli
                    result = run_cli()
                    
                    # Verify the result structure
                    assert result['command'] == 'csv-export'
                    assert result['subcommand'] == 'remove-newlines'
                    assert result['success'] == True
                    
                    # Verify CSV processing was executed (no error means success)
                    # The actual file processing is tested in the CSV export unit tests
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)


if __name__ == "__main__":
    pytest.main([__file__])
