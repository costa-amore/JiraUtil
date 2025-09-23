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


class TestTestFixturePatternParsing:
    """Test pattern parsing functionality for test fixtures."""
    
    def test_parse_summary_pattern_valid_patterns(self):
        """Test parsing valid summary patterns for reset operations."""
        # Test various valid patterns - note: when current status matches target, should_update is False
        test_cases = [
            ("I was in To Do - expected to be in In Progress", "To Do", False, "To Do"),  # Already in target status
            ("I was in In Progress - expected to be in Done", "In Progress", False, "In Progress"),  # Already in target status
            ("I was in Done - expected to be in Closed", "Done", False, "Done"),  # Already in target status
            ("I was in Backlog - expected to be in To Do", "Backlog", False, "Backlog"),  # Already in target status
        ]
        
        for summary, current_status, should_update, target_status in test_cases:
            result = parse_summary_pattern(summary, current_status)
            assert result is not None, f"Should parse pattern: {summary}"
            assert result == (should_update, target_status), f"Should return correct values for: {summary}"
    
    def test_parse_summary_pattern_already_in_target_status(self):
        """Test parsing when issue is already in target status."""
        summary = "I was in To Do - expected to be in In Progress"
        current_status = "To Do"  # Already in target status
        
        result = parse_summary_pattern(summary, current_status)
        assert result == (False, "To Do"), "Should indicate no update needed when already in target status"
    
    def test_parse_summary_pattern_needs_update(self):
        """Test parsing when issue needs to be updated to target status."""
        summary = "I was in To Do - expected to be in In Progress"
        current_status = "In Progress"  # Not in target status, needs update
        
        result = parse_summary_pattern(summary, current_status)
        assert result == (True, "To Do"), "Should indicate update needed when not in target status"
    
    def test_parse_summary_pattern_case_insensitive(self):
        """Test pattern parsing is case insensitive."""
        test_cases = [
            ("i was in to do - expected to be in in progress", "TO DO", False, "to do"),  # Already in target status
            ("I WAS IN IN PROGRESS - EXPECTED TO BE IN DONE", "in progress", False, "IN PROGRESS"),  # Already in target status
            ("I was in DONE - expected to be in CLOSED", "done", False, "DONE"),  # Already in target status
        ]
        
        for summary, current_status, should_update, target_status in test_cases:
            result = parse_summary_pattern(summary, current_status)
            assert result is not None, f"Should parse case insensitive pattern: {summary}"
            assert result == (should_update, target_status), f"Should handle case insensitive matching"
    
    def test_parse_summary_pattern_invalid_patterns(self):
        """Test parsing invalid summary patterns."""
        invalid_patterns = [
            "Regular issue summary",
            "I was in To Do",
            "Expected to be in In Progress",
            "I was in To Do - should be in In Progress",  # Wrong keyword
            "I was To Do - expected to be in In Progress",  # Missing "in"
            "",
            "I was in - expected to be in In Progress",  # Empty status
        ]
        
        for summary in invalid_patterns:
            result = parse_summary_pattern(summary, "To Do")
            assert result is None, f"Should not parse invalid pattern: {summary}"
    
    def test_parse_expectation_pattern_valid_patterns(self):
        """Test parsing valid expectation patterns for assert operations."""
        test_cases = [
            ("I was in To Do - expected to be in In Progress", "To Do", "In Progress"),
            ("I was in In Progress - expected to be in Done", "In Progress", "Done"),
            ("I was in Done - expected to be in Closed", "Done", "Closed"),
        ]
        
        for summary, expected_status1, expected_status2 in test_cases:
            result = parse_expectation_pattern(summary)
            assert result is not None, f"Should parse expectation pattern: {summary}"
            assert result == (expected_status1, expected_status2), f"Should return correct statuses"
    
    def test_parse_expectation_pattern_invalid_patterns(self):
        """Test parsing invalid expectation patterns."""
        invalid_patterns = [
            "Regular issue summary",
            "I was in To Do",
            "Expected to be in In Progress",
            "",
        ]
        
        for summary in invalid_patterns:
            result = parse_expectation_pattern(summary)
            assert result is None, f"Should not parse invalid expectation pattern: {summary}"


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
