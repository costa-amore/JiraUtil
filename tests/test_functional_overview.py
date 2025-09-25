"""
API-focused functional tests for JiraUtil.

This module provides high-level API tests that validate complete
user workflows and application behavior from a user perspective.
"""

import pytest
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock
from .fixtures import (
    create_reset_result, 
    create_assert_result,
    create_temp_csv_file,
    create_temp_env_file,
    create_temp_config_file,
    create_csv_with_embedded_newlines,
    create_csv_for_field_extraction,
    create_csv_with_iso_dates
)

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestJiraUtilAPI:
    """API-focused tests for JiraUtil user workflows."""
    
    def test_user_can_process_csv_files(self):
        """Test that users can process CSV files through the API."""
        # Given: A CSV file with formatting issues that need processing
        csv_with_embedded_newlines = create_temp_csv_file(create_csv_with_embedded_newlines())
        
        # And: Import the required processing functions
        from jira_cleaner import run_remove_newlines
        from csv_utils import run_extract_field_values
        from jira_dates_eu import run as run_jira_dates_eu
        
        try:
            # When: User processes CSV through API
            run_remove_newlines(csv_with_embedded_newlines, None)
            
            # Then: Newlines processing should complete successfully
            newlines_output = csv_with_embedded_newlines.with_name(f"{csv_with_embedded_newlines.stem}-no-newlines.csv")
            assert newlines_output.exists()
            
        finally:
            # Cleanup
            csv_with_embedded_newlines.unlink(missing_ok=True)
            if 'newlines_output' in locals():
                newlines_output.unlink(missing_ok=True)
    
    def test_user_can_extract_field_values_from_csv(self):
        """Test that users can extract field values from CSV files."""
        # Given: A CSV file with structured data for field extraction
        csv_for_field_extraction = create_temp_csv_file(create_csv_for_field_extraction())
        
        # And: Import the required processing function
        from csv_utils import run_extract_field_values
        
        try:
            # When: User extracts field values from CSV
            run_extract_field_values(csv_for_field_extraction, "Status", None)
            
            # Then: Field extraction should complete successfully
            status_output = csv_for_field_extraction.with_name(f"{csv_for_field_extraction.stem}-status.txt")
            assert status_output.exists()
            
        finally:
            # Cleanup
            csv_for_field_extraction.unlink(missing_ok=True)
            if 'status_output' in locals():
                status_output.unlink(missing_ok=True)
    
    def test_user_can_convert_dates_in_csv(self):
        """Test that users can convert date formats in CSV files."""
        # Given: A CSV file with ISO date formats that need conversion
        csv_with_iso_dates = create_temp_csv_file(create_csv_with_iso_dates())
        
        # And: Import the required processing function
        from jira_dates_eu import run as run_jira_dates_eu
        
        try:
            # When: User converts dates in CSV
            run_jira_dates_eu(csv_with_iso_dates, None)
            
            # Then: Date conversion should complete successfully
            dates_output = csv_with_iso_dates.with_name(f"{csv_with_iso_dates.stem}-eu-dates.csv")
            assert dates_output.exists()
            
        finally:
            # Cleanup
            csv_with_iso_dates.unlink(missing_ok=True)
            if 'dates_output' in locals():
                dates_output.unlink(missing_ok=True)
    
    def test_user_can_reset_test_fixtures(self):
        """Test that users can reset test fixtures through the API."""
        # Given: Test fixture reset workflow function and mock Jira instance
        from testfixture.workflow import run_TestFixture_Reset
        
        # When: User runs test fixture reset operation
        with patch('testfixture.workflow.JiraInstanceManager') as mock_manager_class, \
             patch('testfixture.workflow.process_issues_by_label') as mock_process:
            
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_process.return_value = create_reset_result(processed=2, updated=2)
            
            with patch('builtins.print'):
                run_TestFixture_Reset("https://jira.example.com", "user", "pass", "rule-testing")
            
            # Then: Should call appropriate functions
            mock_manager_class.assert_called_once_with("https://jira.example.com", "user", "pass")
            mock_process.assert_called_once_with(mock_manager, "rule-testing")
    
    def test_user_can_assert_test_fixtures(self):
        """Test that users can assert test fixture expectations through the API."""
        # Given: Test fixture assert workflow function and mock Jira instance
        from testfixture.workflow import run_assert_expectations
        
        # When: User runs test fixture assert operation
        with patch('testfixture.workflow.JiraInstanceManager') as mock_manager_class, \
             patch('testfixture.workflow.assert_issues_expectations') as mock_assert:
            
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_assert.return_value = create_assert_result(processed=2, passed=1, failed=1, failures=['PROJ-2: Expected Done but is To Do'])
            
            with patch('builtins.print'):
                run_assert_expectations("https://jira.example.com", "user", "pass", "rule-testing")
            
            # Then: Should call appropriate functions
            mock_manager_class.assert_called_once_with("https://jira.example.com", "user", "pass")
            mock_assert.assert_called_once_with(mock_manager, "rule-testing")
    
    def test_user_can_parse_cli_commands(self):
        """Test that users can parse CLI commands through the API."""
        # Given: CLI parser configured with all available commands
        from cli.parser import build_parser
        
        # When: User parses various commands
        parser = build_parser()
        test_commands = [
            ['csv-export', 'remove-newlines', 'input.csv'],
            ['ce', 'rn', 'input.csv'],
            ['test-fixture', 'reset', 'custom-label'],
            ['tf', 'r'],
            ['list'],
            ['status']
        ]
        
        # Then: All commands should parse successfully
        for cmd in test_commands:
            args = parser.parse_args(cmd)
            assert args.command is not None, f"Command parsing failed for: {cmd}"
    
    def test_user_can_run_list_command(self):
        """Test that users can run the list command through the API."""
        # Given: List command function
        from cli.commands import show_list
        
        # When: User runs list command
        with patch('builtins.print') as mock_print:
            show_list()
        
        # Then: Should display all command categories
        printed_content = ' '.join([str(call) for call in mock_print.call_args_list])
        assert "CSV Export Commands:" in printed_content
        assert "Test Fixture Commands:" in printed_content
        assert "Utility Commands:" in printed_content
        assert "Short Aliases:" in printed_content
    
    def test_user_can_run_status_command(self):
        """Test that users can run the status command through the API."""
        # Given: Status command function
        from cli.commands import show_status
        
        # When: User runs status command
        with patch('builtins.print') as mock_print:
            show_status()
        
        # Then: Should display status information
        printed_content = ' '.join([str(call) for call in mock_print.call_args_list])
        assert "JiraUtil Status" in printed_content
        import re
        version_pattern = r"Version: \d+\.\d+\.\d+"
        assert re.search(version_pattern, printed_content)
        assert "Status: Ready" in printed_content
    
    def test_user_can_get_version(self):
        """Test that users can get version information through the API."""
        # Given: Version manager function
        from version.manager import get_version
        
        # When: User checks version
        version = get_version()
        
        # Then: Should return valid version
        assert version is not None
        assert version != ""
    
    def test_user_can_validate_configuration(self):
        """Test that users can validate configuration through the API."""
        # Given: Configuration validator and template configuration file
        # - Template config contains placeholder values that need to be replaced
        # - Validator function that can detect template patterns
        # - Expected behavior: should identify template values and provide guidance
        from config.validator import check_config_file_for_template_values
        
        # When: User validates template configuration
        template_content = "# Jira Configuration\nJIRA_URL=https://yourcompany.atlassian.net\nJIRA_USERNAME=your.email@example.com\nJIRA_PASSWORD=your_api_token"
        config_path = create_temp_config_file(template_content)
        
        try:
            has_template, message = check_config_file_for_template_values(config_path)
            
            # Then: Should detect template values
            assert has_template is True
            assert "template values" in message
        finally:
            config_path.unlink(missing_ok=True)
    
    def test_user_can_manage_authentication(self):
        """Test that users can manage authentication through the API."""
        # Given: Authentication functions and test environment file
        # - Environment file with valid Jira credentials for testing
        # - Functions for loading environment files and getting credentials
        # - Mock input functions to simulate user interaction
        from auth.credentials import load_env_file, get_jira_credentials
        
        # When: User loads environment file
        env_path = create_temp_env_file("https://test.atlassian.net", "test@example.com", "test_token")
        
        try:
            load_env_file(env_path)
            # Then: Should load without errors
            # Note: We can't easily test os.environ changes in unit tests
            # but we can verify the function doesn't crash
        finally:
            Path(env_path).unlink(missing_ok=True)
        
        # When: User gets credentials interactively
        with patch('builtins.input', side_effect=['https://test.atlassian.net', 'test@example.com']), \
             patch('getpass.getpass', return_value='test_token'), \
             patch('os.getenv', return_value=None):
            
            url, username, password = get_jira_credentials()
            
            # Then: Should return correct credentials
            assert url == 'https://test.atlassian.net'
            assert username == 'test@example.com'
            assert password == 'test_token'
    
    def test_user_can_access_all_modules(self):
        """Test that users can access all modules through the API."""
        # Given: Modular architecture with all required modules available
        # - Core modules: auth, version, config, cli
        # - Feature modules: testfixture, csv_utils
        # - Backward compatibility modules: jira_field_extractor, jira_testfixture
        # When: User imports all modules
        import auth.credentials
        import version.manager
        import config.validator
        import cli.parser
        import cli.commands
        import testfixture.patterns
        import testfixture.issue_processor
        import testfixture.reporter
        import testfixture.workflow
        import csv_utils.field_matcher
        import csv_utils.field_extractor
        
        # When: User imports backward compatibility modules
        import jira_field_extractor
        import jira_testfixture
        
        # When: User accesses main functionality
        from jira_field_extractor import run_extract_field_values
        from jira_testfixture import run_TestFixture_Reset, run_assert_expectations
        
        # Then: All modules should be accessible and callable
        assert callable(run_extract_field_values)
        assert callable(run_TestFixture_Reset)
        assert callable(run_assert_expectations)
    
    def test_user_gets_appropriate_error_handling(self):
        """Test that users get appropriate error handling through the API."""
        # Given: API functions and various error scenarios
        # - Functions that can handle file operations and field extraction
        # - Test cases for nonexistent files, missing fields, and empty files
        # - Expected behavior: graceful error handling with appropriate messages
        from jira_cleaner import run_remove_newlines
        from csv_utils import run_extract_field_values
        from jira_dates_eu import run as run_jira_dates_eu
        
        # When: User tries to process nonexistent file
        nonexistent_file = Path("nonexistent_file.csv")
        
        # Then: Should raise appropriate error
        with pytest.raises(FileNotFoundError):
            run_remove_newlines(nonexistent_file, None)
        
        # When: User tries to extract nonexistent field
        temp_path = create_temp_csv_file("Issue key,Summary\nPROJ-1,Test")
        
        try:
            with patch('builtins.print') as mock_print:
                run_extract_field_values(temp_path, "Nonexistent Field", None)
                
                # Then: Should print warning
                printed_content = ' '.join([str(call) for call in mock_print.call_args_list])
                assert "Warning" in printed_content
                assert "not found" in printed_content
        finally:
            temp_path.unlink(missing_ok=True)
        
        # When: User processes empty file
        temp_path = create_temp_csv_file("")
        
        try:
            # Then: Should handle gracefully
            run_jira_dates_eu(temp_path, None)
        finally:
            temp_path.unlink(missing_ok=True)
    
    def test_user_can_process_large_files(self):
        """Test that users can process large files through the API."""
        # Given: A large CSV file with 100 rows of test data
        # - Each row contains: Issue key, Summary, Parent key, Status, Assignee
        # - Data is structured to test performance with realistic volume
        # - Parent keys are grouped (EPIC-0 to EPIC-9) to test field extraction
        # - Status values cycle through 3 different states
        # - Assignee values cycle through 5 different users
        large_csv_content = "Issue key,Summary,Parent key,Status,Assignee\n"
        for i in range(100):  # 100 rows of test data
            large_csv_content += f"PROJ-{i},Task {i},EPIC-{i//10},Status {i%3},User {i%5}\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_file.write(large_csv_content)
            temp_path = Path(temp_file.name)
        
        try:
            # When: User processes large file
            from jira_cleaner import run_remove_newlines
            from csv_utils import run_extract_field_values
            from jira_dates_eu import run as run_jira_dates_eu
            
            run_remove_newlines(temp_path, None)
            run_extract_field_values(temp_path, "Status", None)
            run_jira_dates_eu(temp_path, None)
            
            # Then: Should complete successfully and create output files
            newlines_output = temp_path.with_name(f"{temp_path.stem}-no-newlines.csv")
            status_output = temp_path.with_name(f"{temp_path.stem}-status.txt")
            dates_output = temp_path.with_name(f"{temp_path.stem}-eu-dates.csv")
            
            assert newlines_output.exists()
            assert status_output.exists()
            assert dates_output.exists()
            
        finally:
            temp_path.unlink(missing_ok=True)
            newlines_output.unlink(missing_ok=True)
            status_output.unlink(missing_ok=True)
            dates_output.unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
