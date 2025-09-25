"""
Functional tests for test fixture commands.

This module tests the complete test fixture functionality including:
- test-fixture reset command
- test-fixture assert command
- Pattern parsing and issue processing
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from testfixture.workflow import run_TestFixture_Reset, run_assert_expectations
from testfixture.patterns import parse_summary_pattern, parse_expectation_pattern
from testfixture.issue_processor import process_issues_by_label, assert_issues_expectations
from jira_manager import JiraInstanceManager


class TestIssueSummaryPatternParsing:
    """Test issue summary pattern parsing functionality for test fixtures."""
    
    def test_issue_summary_pattern_parsing(self):
        """Test comprehensive issue summary pattern parsing for all supported formats."""
        # Test all valid issue summary patterns
        issue_summary_test_cases = [
            # Format 1: "I was in <status1> - expected to be in <status2>"
            ("I was in To Do - expected to be in In Progress", "To Do", "In Progress"),
            
            # Format 2: "[<context> - ]starting in <status1> - expected to be in <status2>"
            ("Bug fix - starting in To Do - expected to be in In Progress", "To Do", "In Progress"),  # With context
            ("starting in To Do - expected to be in In Progress", "To Do", "In Progress"),  # Without context
            
            # Case insensitive
            ("i was in to do - expected to be in in progress", "to do", "in progress"),
            ("BUG FIX - STARTING IN TO DO - EXPECTED TO BE IN IN PROGRESS", "TO DO", "IN PROGRESS"),
            
            # More permissive patterns (anything before key phrases is ignored)
            ("Context starting in To Do - expected to be in In Progress", "To Do", "In Progress"),
            ("Some random text before starting in Done - expected to be in Closed", "Done", "Closed"),
        ]
        
        for issue_summary, expected_status1, expected_status2 in issue_summary_test_cases:
            # Test summary pattern parsing (for reset operations)
            summary_result = parse_summary_pattern(issue_summary)
            assert summary_result is not None, f"Should parse issue summary pattern: {issue_summary}"
            assert summary_result == (expected_status1, expected_status2), f"Should return correct summary values for: {issue_summary}"
            
            # Test expectation pattern parsing (for assert operations)
            expectation_result = parse_expectation_pattern(issue_summary)
            assert expectation_result is not None, f"Should parse expectation pattern: {issue_summary}"
            assert expectation_result == (expected_status1, expected_status2), f"Should return correct expectation values for: {issue_summary}"
    
    def test_invalid_issue_summary_patterns(self):
        """Test that invalid issue summary patterns are rejected (case insensitive)."""
        invalid_issue_summary_patterns = [
            "Regular issue summary",
            "I was in To Do",  # Missing expected part
            "i was in to do",  # Case insensitive - missing expected part
            "Expected to be in In Progress",  # Missing I was in part
            "expected to be in in progress",  # Case insensitive - missing I was in part
            "I was in To Do expected to be in In Progress",  # Missing " - "
            "i was in to do expected to be in in progress",  # Case insensitive - missing " - "
            "I was To Do - expected to be in In Progress",  # Missing "in"
            "i was to do - expected to be in in progress",  # Case insensitive - missing "in"
            "I was in - expected to be in In Progress",  # Empty status
            "i was in - expected to be in in progress",  # Case insensitive - empty status
            "",  # Empty string
        ]
        
        for invalid_issue_summary in invalid_issue_summary_patterns:
            summary_result = parse_summary_pattern(invalid_issue_summary)
            expectation_result = parse_expectation_pattern(invalid_issue_summary)
            assert summary_result is None, f"Should not parse invalid issue summary pattern: '{invalid_issue_summary}'"
            assert expectation_result is None, f"Should not parse invalid expectation pattern: '{invalid_issue_summary}'"


class TestTestFixtureResetCommand:
    """Test the test-fixture reset command functionality."""
    
    def test_reset_command_successful_processing(self):
        """Test successful reset processing with mock Jira."""
        # Mock Jira manager and issues - use different current statuses so updates are needed
        mock_manager = Mock(spec=JiraInstanceManager)
        mock_manager.jira = None  # Set to None so connect() will be called
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
        
        # Test the processing function directly
        result = process_issues_by_label(mock_manager, "rule-testing")
        
        # Verify results
        assert result['success'] is True
        assert result['processed'] == 2
        assert result['updated'] == 2
        assert result['skipped'] == 0
        assert len(result['errors']) == 0
        
        # Verify manager methods were called
        mock_manager.connect.assert_called_once()
        mock_manager.get_issues_by_label.assert_called_once_with("rule-testing")
        assert mock_manager.update_issue_status.call_count == 2
    
    def test_reset_command_skips_already_correct_status(self):
        """Test reset command skips issues already in target status."""
        mock_manager = Mock(spec=JiraInstanceManager)
        mock_manager.jira = Mock()
        mock_manager.connect.return_value = True
        mock_manager.get_issues_by_label.return_value = [
            {
                'key': 'PROJ-1',
                'summary': 'I was in To Do - expected to be in In Progress',
                'status': 'To Do'  # Already in target status
            }
        ]
        
        with patch('testfixture.issue_processor.JiraInstanceManager', return_value=mock_manager):
            result = process_issues_by_label(mock_manager, "rule-testing")
        
        assert result['success'] is True
        assert result['processed'] == 1
        assert result['updated'] == 0
        assert result['skipped'] == 1
        mock_manager.update_issue_status.assert_not_called()
    
    def test_reset_command_skips_invalid_patterns(self):
        """Test reset command skips issues with invalid summary patterns."""
        mock_manager = Mock(spec=JiraInstanceManager)
        mock_manager.jira = Mock()
        mock_manager.connect.return_value = True
        mock_manager.get_issues_by_label.return_value = [
            {
                'key': 'PROJ-1',
                'summary': 'Regular issue summary',  # Invalid pattern
                'status': 'To Do'
            },
            {
                'key': 'PROJ-2',
                'summary': 'I was in To Do - expected to be in In Progress',
                'status': 'In Progress'  # Different from target status, needs update
            }
        ]
        mock_manager.update_issue_status.return_value = True
        
        with patch('testfixture.issue_processor.JiraInstanceManager', return_value=mock_manager):
            result = process_issues_by_label(mock_manager, "rule-testing")
        
        assert result['success'] is True
        assert result['processed'] == 2
        assert result['updated'] == 1
        assert result['skipped'] == 1
        mock_manager.update_issue_status.assert_called_once()
    
    def test_reset_command_handles_connection_failure(self):
        """Test reset command handles Jira connection failure."""
        mock_manager = Mock(spec=JiraInstanceManager)
        mock_manager.jira = None
        mock_manager.connect.return_value = False
        
        with patch('testfixture.issue_processor.JiraInstanceManager', return_value=mock_manager):
            result = process_issues_by_label(mock_manager, "rule-testing")
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Failed to connect to Jira' in result['error']
    
    def test_reset_command_handles_no_issues(self):
        """Test reset command handles case with no issues found."""
        mock_manager = Mock(spec=JiraInstanceManager)
        mock_manager.jira = Mock()
        mock_manager.connect.return_value = True
        mock_manager.get_issues_by_label.return_value = []
        
        with patch('testfixture.issue_processor.JiraInstanceManager', return_value=mock_manager):
            result = process_issues_by_label(mock_manager, "rule-testing")
        
        assert result['success'] is True
        assert result['processed'] == 0
        assert result['updated'] == 0
        assert result['skipped'] == 0


class TestTestFixtureAssertCommand:
    """Test the test-fixture assert command functionality."""
    
    def test_assert_command_successful_assertions(self):
        """Test successful assertion processing with mock Jira."""
        mock_manager = Mock(spec=JiraInstanceManager)
        mock_manager.jira = Mock()
        mock_manager.connect.return_value = True
        mock_manager.get_issues_by_label.return_value = [
            {
                'key': 'PROJ-1',
                'summary': 'I was in To Do - expected to be in In Progress',
                'status': 'In Progress'  # Matches expected status
            },
            {
                'key': 'PROJ-2',
                'summary': 'I was in In Progress - expected to be in Done',
                'status': 'Done'  # Matches expected status
            }
        ]
        
        with patch('testfixture.issue_processor.JiraInstanceManager', return_value=mock_manager):
            result = assert_issues_expectations(mock_manager, "rule-testing")
        
        assert result['success'] is True
        assert result['processed'] == 2
        assert result['passed'] == 2
        assert result['failed'] == 0
        assert result['not_evaluated'] == 0
        assert len(result['failures']) == 0
    
    def test_assert_command_detects_failures(self):
        """Test assertion command detects status mismatches."""
        mock_manager = Mock(spec=JiraInstanceManager)
        mock_manager.jira = Mock()
        mock_manager.connect.return_value = True
        mock_manager.get_issues_by_label.return_value = [
            {
                'key': 'PROJ-1',
                'summary': 'I was in To Do - expected to be in In Progress',
                'status': 'To Do'  # Does not match expected status
            },
            {
                'key': 'PROJ-2',
                'summary': 'I was in In Progress - expected to be in Done',
                'status': 'Done'  # Matches expected status
            }
        ]
        
        with patch('testfixture.issue_processor.JiraInstanceManager', return_value=mock_manager):
            result = assert_issues_expectations(mock_manager, "rule-testing")
        
        assert result['success'] is True
        assert result['processed'] == 2
        assert result['passed'] == 1
        assert result['failed'] == 1
        assert result['not_evaluated'] == 0
        assert len(result['failures']) == 1
        assert 'PROJ-1' in result['failures'][0]
    
    def test_assert_command_skips_invalid_patterns(self):
        """Test assertion command skips issues with invalid summary patterns."""
        mock_manager = Mock(spec=JiraInstanceManager)
        mock_manager.jira = Mock()
        mock_manager.connect.return_value = True
        mock_manager.get_issues_by_label.return_value = [
            {
                'key': 'PROJ-1',
                'summary': 'Regular issue summary',  # Invalid pattern
                'status': 'To Do'
            },
            {
                'key': 'PROJ-2',
                'summary': 'I was in To Do - expected to be in In Progress',
                'status': 'In Progress'
            }
        ]
        
        with patch('testfixture.issue_processor.JiraInstanceManager', return_value=mock_manager):
            result = assert_issues_expectations(mock_manager, "rule-testing")
        
        assert result['success'] is True
        assert result['processed'] == 2
        assert result['passed'] == 1
        assert result['failed'] == 0
        assert result['not_evaluated'] == 1
        assert 'PROJ-1' in result['not_evaluated_keys']
    
    def test_assert_command_handles_connection_failure(self):
        """Test assertion command handles Jira connection failure."""
        mock_manager = Mock(spec=JiraInstanceManager)
        mock_manager.jira = None
        mock_manager.connect.return_value = False
        
        with patch('testfixture.issue_processor.JiraInstanceManager', return_value=mock_manager):
            result = assert_issues_expectations(mock_manager, "rule-testing")
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Failed to connect to Jira' in result['error']
    
    def test_assert_command_handles_no_issues(self):
        """Test assertion command handles case with no issues found."""
        mock_manager = Mock(spec=JiraInstanceManager)
        mock_manager.jira = Mock()
        mock_manager.connect.return_value = True
        mock_manager.get_issues_by_label.return_value = []
        
        with patch('testfixture.issue_processor.JiraInstanceManager', return_value=mock_manager):
            result = assert_issues_expectations(mock_manager, "rule-testing")
        
        assert result['success'] is True
        assert result['processed'] == 0
        assert result['passed'] == 0
        assert result['failed'] == 0
        assert result['not_evaluated'] == 0


class TestTestFixtureWorkflowIntegration:
    """Test the complete workflow integration for test fixture commands."""
    
    @patch('testfixture.workflow.JiraInstanceManager')
    @patch('testfixture.workflow.process_issues_by_label')
    def test_reset_workflow_integration(self, mock_process, mock_manager_class):
        """Test complete reset workflow integration."""
        # Setup mocks
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_process.return_value = {
            'success': True,
            'processed': 2,
            'updated': 1,
            'skipped': 1,
            'errors': []
        }
        
        # Test the workflow function
        with patch('builtins.print') as mock_print:
            run_TestFixture_Reset("https://jira.example.com", "user", "pass", "rule-testing")
        
        # Verify manager was created with correct parameters
        mock_manager_class.assert_called_once_with("https://jira.example.com", "user", "pass")
        
        # Verify processing was called
        mock_process.assert_called_once_with(mock_manager, "rule-testing")
        
        # Verify output was printed
        assert mock_print.call_count >= 3  # At least 3 print statements expected
    
    @patch('testfixture.workflow.JiraInstanceManager')
    @patch('testfixture.workflow.assert_issues_expectations')
    def test_assert_workflow_integration(self, mock_assert, mock_manager_class):
        """Test complete assert workflow integration."""
        # Setup mocks
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_assert.return_value = {
            'success': True,
            'processed': 2,
            'passed': 2,
            'failed': 0,
            'not_evaluated': 0,
            'failures': [],
            'not_evaluated_keys': []
        }
        
        # Test the workflow function
        with patch('builtins.print') as mock_print:
            run_assert_expectations("https://jira.example.com", "user", "pass", "rule-testing")
        
        # Verify manager was created with correct parameters
        mock_manager_class.assert_called_once_with("https://jira.example.com", "user", "pass")
        
        # Verify assertion was called
        mock_assert.assert_called_once_with(mock_manager, "rule-testing")
        
        # Verify output was printed
        assert mock_print.call_count >= 3  # At least 3 print statements expected


if __name__ == "__main__":
    pytest.main([__file__])
