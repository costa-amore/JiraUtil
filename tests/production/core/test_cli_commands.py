"""
Tests for CLI commands.
"""

import pytest
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from io import StringIO

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))
# Add tests directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from cli.parser import build_parser
from cli.commands import show_list, show_status
from version.manager import get_version
from config.validator import check_config_file_for_template_values, get_config_file_status_message
from tests.fixtures import (create_temp_config_file, create_temp_env_file, generate_env_content, 
                       TEMPLATE_CONFIG_CONTENT, CONFIGURED_CONFIG_CONTENT, 
                       CSV_EXPORT_COMMANDS, TEST_FIXTURE_SINGLE_COMMANDS, TEST_FIXTURE_CHAINED_COMMANDS, UTILITY_COMMANDS)


class TestCLICommands:
    """Test CLI command functionality."""
    
    def test_list_command_displays_all_commands(self):
        """Test that list command displays all available commands."""
        with patch('builtins.print') as mock_print:
            show_list()
        
        printed_content = ' '.join([str(call) for call in mock_print.call_args_list])
        
        # Verify all major command categories are displayed
        expected_sections = [
            "CSV Export Commands:", "Test Fixture Commands:", "Utility Commands:", "Short Aliases:"
        ]
        for section in expected_sections:
            assert section in printed_content, f"Missing section: {section}"
        
        # Verify specific commands
        expected_commands = [
            "csv-export remove-newlines", "test-fixture reset", "list", "status", "--version", "--help"
        ]
        for command in expected_commands:
            assert command in printed_content, f"Missing command: {command}"
        
        # Verify aliases
        expected_aliases = ["ce rn", "tf r", "ls", "st"]
        for alias in expected_aliases:
            assert alias in printed_content, f"Missing alias: {alias}"
        
        # Verify formatting
        assert mock_print.call_count >= 20, "Should have multiple print statements for formatting"
        printed_lines = [str(call) for call in mock_print.call_args_list]
        assert any("=" in line for line in printed_lines), "Should have separator lines"
        assert any("JiraUtil - Available Commands" in line for line in printed_lines), "Should have main header"


    def test_status_command_displays_basic_info(self):
        """Test that status command displays basic tool information."""
        with patch('builtins.print') as mock_print, \
             patch('version.manager.get_version', return_value="1.0.24"):
            show_status()
        
        printed_content = ' '.join([str(call) for call in mock_print.call_args_list])
        
        # Verify basic information is displayed
        expected_content = [
            "JiraUtil Status", "Status: Ready", "Configuration:", "Default test-set-label: rule-testing"
        ]
        for content in expected_content:
            assert content in printed_content, f"Missing content: {content}"
        
        # Test for version pattern
        import re
        version_pattern = r"Version: \d+\.\d+\.\d+"
        assert re.search(version_pattern, printed_content), f"Version pattern not found in: {printed_content}"
    
    def test_status_command_config_scenarios(self):
        """Test status command in different config scenarios."""
        # Test executable mode (no config file)
        with patch('builtins.print') as mock_print, \
             patch('version.manager.get_version', return_value="1.0.24"), \
             patch('version.manager.is_frozen', return_value=True), \
             patch('pathlib.Path.exists', return_value=False):
            show_status()
        
        printed_content = ' '.join([str(call) for call in mock_print.call_args_list])
        assert "jira_config.env not found" in printed_content
        assert "needs to be created" in printed_content
        
        # Test development mode (no config file)
        with patch('builtins.print') as mock_print, \
             patch('version.manager.get_version', return_value="1.0.24"), \
             patch('version.manager.is_frozen', return_value=False), \
             patch('pathlib.Path.exists', return_value=False):
            show_status()
        
        printed_content = ' '.join([str(call) for call in mock_print.call_args_list])
        assert "No config file found" in printed_content
        assert ".venv/jira_config.env" in printed_content


    def test_version_command_scenarios(self):
        """Test version command in different scenarios."""
        # Test development mode with version file
        with patch('version.manager.is_frozen', return_value=False), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data='{"major": 1, "minor": 0, "build": 24}')):
            
            version = get_version()
            assert version == "1.0.24"
        
        # Test fallback when version detection fails
        with patch('version.manager.is_frozen', return_value=False), \
             patch('pathlib.Path.exists', return_value=False):
            
            version = get_version()
            assert version == "unknown"


    def test_parser_creation(self):
        """Test that argument parser is created correctly."""
        parser = build_parser()
        
        assert parser.prog == "JiraUtil"
        assert parser.description == "Jira utilities"
        
        # Test that subcommands exist
        subcommands = [action.dest for action in parser._actions if hasattr(action, 'dest') and action.dest == 'command']
        assert 'command' in subcommands
    
    def test_csv_export_command_parsing(self):
        """Test CSV export command parsing."""
        parser = build_parser()
        
        for args_list, expected_command, expected_subcommand, expected_input in CSV_EXPORT_COMMANDS:
            args = parser.parse_args(args_list)
            assert args.command == expected_command
            assert args.csv_command == expected_subcommand
            assert args.input == expected_input
    
    def test_testfixture_single_command_parsing(self):
        """Test test fixture single command parsing."""
        parser = build_parser()
        
        for args_list, expected_command, expected_subcommand, expected_label in TEST_FIXTURE_SINGLE_COMMANDS:
            args = parser.parse_args(args_list)
            assert args.command == expected_command
            assert args.commands == [expected_subcommand]
            assert args.tsl == expected_label
    
    def test_testfixture_chained_command_parsing(self):
        """Test test fixture chained command parsing."""
        parser = build_parser()
        
        for args_list, expected_command, expected_subcommands, expected_label in TEST_FIXTURE_CHAINED_COMMANDS:
            args = parser.parse_args(args_list)
            assert args.command == expected_command
            assert args.commands == expected_subcommands
            assert args.tsl == expected_label
    
    def test_utility_command_parsing(self):
        """Test utility command parsing."""
        parser = build_parser()
        
        for args_list, expected_command in UTILITY_COMMANDS:
            args = parser.parse_args(args_list)
            assert args.command == expected_command
    
    def test_version_and_help_options(self):
        """Test version and help options."""
        parser = build_parser()
        
        # Test version option
        with pytest.raises(SystemExit):  # --version causes sys.exit
            parser.parse_args(['--version'])
        
        # Test help option
        with pytest.raises(SystemExit):  # --help causes sys.exit
            parser.parse_args(['--help'])


    def test_config_file_validation(self):
        """Test configuration file validation."""
        # Test template values detected using flexible generator
        config_path = create_temp_env_file("https://yourcompany.atlassian.net", "your.email@example.com", "your_api_token_here")
        try:
            has_template, message = check_config_file_for_template_values(config_path)
            assert has_template is True
            assert "template values" in message
            assert "needs configuration" in message
        finally:
            config_path.unlink(missing_ok=True)
        
        # Test no template values using flexible generator
        config_path = create_temp_env_file("https://mycompany.atlassian.net", "john.doe@mycompany.com", "abc123def456ghi789")
        try:
            has_template, message = check_config_file_for_template_values(config_path)
            assert has_template is False
            assert "appears to be configured" in message
        finally:
            config_path.unlink(missing_ok=True)
    
    def test_config_status_messages(self):
        """Test configuration status message generation."""
        config_path = Path("test_config.env")
        
        # Test template values message
        with patch('config.validator.check_config_file_for_template_values', return_value=(True, "Template detected")):
            message = get_config_file_status_message(config_path)
            assert "Jira credentials: Template detected" in message
        
        # Test configured message
        with patch('config.validator.check_config_file_for_template_values', return_value=(False, "Configured")):
            message = get_config_file_status_message(config_path, is_venv_config=True)
            assert "Jira credentials: Configured" in message


    def test_cli_integration_scenarios(self):
        """Test CLI integration scenarios."""
        # Test help command
        with patch('sys.argv', ['JiraUtil.py', '--help']):
            with patch('builtins.print'):
                from src.JiraUtil import run_cli
                try:
                    run_cli()
                    assert False, "Expected SystemExit for help command"
                except SystemExit as e:
                    assert e.code == 0, f"Expected exit code 0, got {e.code}"
        
        # Test list command
        with patch('sys.argv', ['JiraUtil.py', 'list']):
            with patch('builtins.print') as mock_print:
                from src.JiraUtil import run_cli
                result = run_cli()
                
                assert result['command'] == 'list'
                assert result['success'] == True
                
                printed_content = ' '.join([str(call) for call in mock_print.call_args_list])
                assert "JiraUtil - Available Commands" in printed_content
        
        # Test status command
        with patch('sys.argv', ['JiraUtil.py', 'status']):
            with patch('builtins.print') as mock_print, \
                 patch('version.manager.get_version', return_value="1.0.24"), \
                 patch('version.manager.is_frozen', return_value=False), \
                 patch('pathlib.Path.exists', return_value=False):
                from src.JiraUtil import run_cli
                result = run_cli()
                
                assert result['command'] == 'status'
                assert result['success'] == True
                
                printed_content = ' '.join([str(call) for call in mock_print.call_args_list])
                assert "JiraUtil Status" in printed_content
        
        # Test CSV export command
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_file.write("Name,Description\nTest,Line1\nLine2")
            temp_file_path = temp_file.name
        
        try:
            with patch('sys.argv', ['JiraUtil.py', 'csv-export', 'remove-newlines', temp_file_path]):
                with patch('builtins.print'):
                    from src.JiraUtil import run_cli
                    result = run_cli()
                    
                    assert result['command'] == 'csv-export'
                    assert result['subcommand'] == 'remove-newlines'
                    assert result['success'] == True
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)


if __name__ == "__main__":
    pytest.main([__file__])
