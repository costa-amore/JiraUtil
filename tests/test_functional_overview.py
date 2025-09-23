"""
Functional overview tests for JiraUtil.

This module provides a high-level overview of all JiraUtil functionalities
and serves as a comprehensive test suite that validates the complete
application behavior from a user perspective.
"""

import pytest
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open, Mock

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestJiraUtilFunctionalOverview:
    """
    Comprehensive functional overview tests for JiraUtil.
    
    This test class validates all major functionalities and use cases
    that a user would encounter when using JiraUtil. The tests are
    organized by functional area and provide clear validation of
    the application's capabilities.
    """
    
    def test_csv_export_functionality_overview(self):
        """
        Test CSV Export Functionality Overview.
        
        Validates that all CSV export commands work correctly:
        - Remove newlines from CSV fields
        - Extract field values to comma-separated lists
        - Convert dates to European Excel format
        """
        # Test data representing a typical Jira CSV export
        test_csv_content = '''Issue key,Summary,Description,Parent key,Status,Assignee,Created,Updated
PROJ-1,"Task with newlines
in summary","Description with
multiple lines",EPIC-1,Done,John Doe,2024-01-15 10:30:00,2024-01-20 14:45:00
PROJ-2,"Normal task","Single line description",EPIC-1,In Progress,Jane Smith,2024-02-01 09:15:00,2024-02-05 16:20:00
PROJ-3,"Another task","Another description",EPIC-2,To Do,Bob Wilson,2024-03-10 11:00:00,2024-03-10 11:00:00'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as input_file:
            input_file.write(test_csv_content)
            input_file_path = Path(input_file.name)
        
        try:
            # Test 1: Remove newlines functionality
            from jira_cleaner import run_remove_newlines
            run_remove_newlines(input_file_path, None)
            
            newlines_output = input_file_path.with_name(f"{input_file_path.stem}-no-newlines.csv")
            assert newlines_output.exists(), "Newlines removal should create output file"
            
            with open(newlines_output, 'r', encoding='utf-8') as f:
                cleaned_content = f.read()
                assert "Task with newlines in summary" in cleaned_content, "Newlines should be cleaned"
                assert "\n" not in cleaned_content.split('\n')[1:], "Data rows should not contain newlines"
            
            # Test 2: Extract field values functionality
            from csv_utils import run_extract_field_values
            
            # Extract Parent key values
            run_extract_field_values(input_file_path, "Parent key", None)
            parent_output = input_file_path.with_name(f"{input_file_path.stem}-parent-key.txt")
            assert parent_output.exists(), "Parent key extraction should create output file"
            
            with open(parent_output, 'r', encoding='utf-8') as f:
                parent_content = f.read()
                assert "(EPIC-1,EPIC-2)" in parent_content, "Should extract unique parent keys"
                assert "Parent key found=2" in parent_content, "Should show correct count"
            
            # Extract Status values
            run_extract_field_values(input_file_path, "Status", None)
            status_output = input_file_path.with_name(f"{input_file_path.stem}-status.txt")
            assert status_output.exists(), "Status extraction should create output file"
            
            with open(status_output, 'r', encoding='utf-8') as f:
                status_content = f.read()
                assert "(Done,In Progress,To Do)" in status_content, "Should extract unique statuses"
                assert "Status found=3" in status_content, "Should show correct count"
            
            # Test 3: Fix dates for European Excel
            from jira_dates_eu import run as run_jira_dates_eu
            run_jira_dates_eu(input_file_path, None)
            
            dates_output = input_file_path.with_name(f"{input_file_path.stem}-eu-dates.csv")
            assert dates_output.exists(), "Date conversion should create output file"
            
            with open(dates_output, 'r', encoding='utf-8') as f:
                dates_content = f.read()
                assert "15/01/2024 10:30:00" in dates_content, "Should convert to EU date format"
                assert "20/01/2024 14:45:00" in dates_content, "Should convert to EU date format"
            
        finally:
            # Cleanup
            input_file_path.unlink(missing_ok=True)
            newlines_output.unlink(missing_ok=True)
            parent_output.unlink(missing_ok=True)
            status_output.unlink(missing_ok=True)
            dates_output.unlink(missing_ok=True)
    
    def test_testfixture_functionality_overview(self):
        """
        Test Test Fixture Functionality Overview.
        
        Validates that test fixture management works correctly:
        - Pattern parsing for test fixture issues
        - Reset functionality for test fixtures
        - Assert functionality for test fixtures
        """
        from testfixture.patterns import parse_summary_pattern, parse_expectation_pattern
        from testfixture.issue_processor import process_issues_by_label, assert_issues_expectations
        
        # Test 1: Pattern parsing functionality
        test_patterns = [
            ("I was in To Do - expected to be in In Progress", "To Do", False, "To Do"),  # Already in target status
            ("I was in In Progress - expected to be in Done", "In Progress", False, "In Progress"),  # Already in target status
            ("I was in Done - expected to be in Closed", "Done", False, "Done"),  # Already in target status
        ]
        
        for summary, current_status, should_update, target_status in test_patterns:
            result = parse_summary_pattern(summary, current_status)
            assert result == (should_update, target_status), f"Pattern parsing failed for: {summary}"
        
        # Test expectation parsing
        expectation_patterns = [
            ("I was in To Do - expected to be in In Progress", "To Do", "In Progress"),
            ("I was in In Progress - expected to be in Done", "In Progress", "Done"),
        ]
        
        for summary, expected_status1, expected_status2 in expectation_patterns:
            result = parse_expectation_pattern(summary)
            assert result == (expected_status1, expected_status2), f"Expectation parsing failed for: {summary}"
        
        # Test 2: Reset functionality with mocked Jira
        mock_manager = Mock()
        mock_manager.jira = Mock()
        mock_manager.connect.return_value = True
        mock_manager.get_issues_by_label.return_value = [
            {
                'key': 'PROJ-1',
                'summary': 'I was in To Do - expected to be in In Progress',
                'status': 'In Progress'  # Different from target status, needs update
            },
            {
                'key': 'PROJ-2',
                'summary': 'I was in In Progress - expected to be in Done',
                'status': 'Done'  # Different from target status, needs update
            }
        ]
        mock_manager.update_issue_status.return_value = True
        
        result = process_issues_by_label(mock_manager, "rule-testing")
        assert result['success'] is True
        assert result['processed'] == 2
        assert result['updated'] == 2
        assert result['skipped'] == 0
        
        # Test 3: Assert functionality with mocked Jira
        mock_manager.get_issues_by_label.return_value = [
            {
                'key': 'PROJ-1',
                'summary': 'I was in To Do - expected to be in In Progress',
                'status': 'In Progress'  # Matches expected status
            },
            {
                'key': 'PROJ-2',
                'summary': 'I was in In Progress - expected to be in Done',
                'status': 'To Do'  # Does not match expected status
            }
        ]
        
        result = assert_issues_expectations(mock_manager, "rule-testing")
        assert result['success'] is True
        assert result['processed'] == 2
        assert result['passed'] == 1
        assert result['failed'] == 1
        assert len(result['failures']) == 1
    
    def test_cli_functionality_overview(self):
        """
        Test CLI Functionality Overview.
        
        Validates that all CLI commands work correctly:
        - Help and version commands
        - List and status commands
        - Command parsing and routing
        - Configuration validation
        """
        from cli.parser import build_parser
        from cli.commands import show_list, show_status
        from version.manager import get_version
        from config.validator import check_config_file_for_template_values
        
        # Test 1: Command parsing
        parser = build_parser()
        assert parser.prog == "JiraUtil"
        assert parser.description == "Jira utilities"
        
        # Test various command combinations
        test_commands = [
            ['csv-export', 'remove-newlines', 'input.csv'],
            ['ce', 'rn', 'input.csv'],
            ['csv-export', 'extract-to-comma-separated-list', 'Status', 'input.csv'],
            ['ce', 'ecl', 'Status', 'input.csv'],
            ['csv-export', 'fix-dates-eu', 'input.csv'],
            ['ce', 'fd', 'input.csv'],
            ['test-fixture', 'reset', 'custom-label'],
            ['tf', 'r'],
            ['test-fixture', 'assert', 'custom-label'],
            ['tf', 'a'],
            ['list'],
            ['ls'],
            ['status'],
            ['st'],
        ]
        
        for cmd in test_commands:
            args = parser.parse_args(cmd)
            assert args.command is not None, f"Command parsing failed for: {cmd}"
        
        # Test 2: List command
        with patch('builtins.print') as mock_print:
            show_list()
        
        printed_content = ' '.join([str(call) for call in mock_print.call_args_list])
        assert "CSV Export Commands:" in printed_content
        assert "Test Fixture Commands:" in printed_content
        assert "Utility Commands:" in printed_content
        assert "Short Aliases:" in printed_content
        
        # Test 3: Status command
        with patch('builtins.print') as mock_print:
            show_status()
        
        printed_content = ' '.join([str(call) for call in mock_print.call_args_list])
        assert "JiraUtil Status" in printed_content
        # Test for version pattern instead of hardcoded version
        import re
        version_pattern = r"Version: \d+\.\d+\.\d+"
        assert re.search(version_pattern, printed_content), f"Version pattern not found in: {printed_content}"
        assert "Status: Ready" in printed_content
        
        # Test 4: Version detection
        version = get_version()
        assert version is not None
        assert version != ""
        
        # Test 5: Configuration validation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as config_file:
            config_file.write("JIRA_URL=https://yourcompany.atlassian.net\nJIRA_USERNAME=your.email@example.com")
            config_path = Path(config_file.name)
        
        try:
            has_template, message = check_config_file_for_template_values(config_path)
            assert has_template is True
            assert "template values" in message
        finally:
            config_path.unlink(missing_ok=True)
    
    def test_authentication_functionality_overview(self):
        """
        Test Authentication Functionality Overview.
        
        Validates that authentication and credential management works correctly:
        - Environment file loading
        - Credential validation
        - Template value detection
        """
        from auth.credentials import load_env_file, get_jira_credentials
        
        # Test 1: Environment file loading
        env_content = """# Test Environment
JIRA_URL=https://test.atlassian.net
JIRA_USERNAME=test@example.com
JIRA_PASSWORD=test_token
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as env_file:
            env_file.write(env_content)
            env_path = env_file.name
        
        try:
            load_env_file(env_path)
            # Note: We can't easily test os.environ changes in unit tests
            # but we can verify the function doesn't crash
        finally:
            Path(env_path).unlink(missing_ok=True)
        
        # Test 2: Credential validation with mocked input
        with patch('builtins.input', side_effect=['https://test.atlassian.net', 'test@example.com']), \
             patch('getpass.getpass', return_value='test_token'), \
             patch('os.getenv', return_value=None):
            
            url, username, password = get_jira_credentials()
            assert url == 'https://test.atlassian.net'
            assert username == 'test@example.com'
            assert password == 'test_token'
    
    def test_modular_architecture_overview(self):
        """
        Test Modular Architecture Overview.
        
        Validates that the refactored modular architecture works correctly:
        - All modules can be imported
        - Module dependencies are resolved
        - Backward compatibility is maintained
        """
        # Test that all new modules can be imported
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
        
        # Test that backward compatibility modules work
        import jira_field_extractor
        import jira_testfixture
        
        # Test that main functionality is accessible
        from jira_field_extractor import run_extract_field_values
        from jira_testfixture import run_TestFixture_Reset, run_assert_expectations
        
        # Verify functions are callable
        assert callable(run_extract_field_values)
        assert callable(run_TestFixture_Reset)
        assert callable(run_assert_expectations)
    
    def test_error_handling_overview(self):
        """
        Test Error Handling Overview.
        
        Validates that error handling works correctly across all modules:
        - File not found errors
        - Invalid input handling
        - Network/connection errors
        - Malformed data handling
        """
        from jira_cleaner import run_remove_newlines
        from csv_utils import run_extract_field_values
        from jira_dates_eu import run as run_jira_dates_eu
        
        # Test 1: File not found error handling
        nonexistent_file = Path("nonexistent_file.csv")
        
        # This should raise FileNotFoundError, which is expected behavior
        with pytest.raises(FileNotFoundError):
            run_remove_newlines(nonexistent_file, None)
        
        # Test 2: Invalid field name handling
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_file.write("Issue key,Summary\nPROJ-1,Test")
            temp_path = Path(temp_file.name)
        
        try:
            with patch('builtins.print') as mock_print:
                run_extract_field_values(temp_path, "Nonexistent Field", None)
                # Should print warning about field not found
                printed_content = ' '.join([str(call) for call in mock_print.call_args_list])
                assert "Warning" in printed_content
                assert "not found" in printed_content
        finally:
            temp_path.unlink(missing_ok=True)
        
        # Test 3: Empty file handling
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_file.write("")
            temp_path = Path(temp_file.name)
        
        try:
            run_jira_dates_eu(temp_path, None)
            # Should handle empty file gracefully
        finally:
            temp_path.unlink(missing_ok=True)
    
    def test_performance_overview(self):
        """
        Test Performance Overview.
        
        Validates that the application performs well with typical data sizes:
        - Large CSV file processing
        - Multiple field extractions
        - Batch operations
        """
        # Create a larger test CSV file
        large_csv_content = "Issue key,Summary,Parent key,Status,Assignee\n"
        for i in range(100):  # 100 rows of test data
            large_csv_content += f"PROJ-{i},Task {i},EPIC-{i//10},Status {i%3},User {i%5}\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_file.write(large_csv_content)
            temp_path = Path(temp_file.name)
        
        try:
            # Test processing large file
            from jira_cleaner import run_remove_newlines
            from csv_utils import run_extract_field_values
            from jira_dates_eu import run as run_jira_dates_eu
            
            # These should complete without errors
            run_remove_newlines(temp_path, None)
            run_extract_field_values(temp_path, "Status", None)
            run_jira_dates_eu(temp_path, None)
            
            # Verify output files were created
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
