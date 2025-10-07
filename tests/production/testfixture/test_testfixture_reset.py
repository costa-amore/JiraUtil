"""
Tests for test fixture reset operations.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
# Add tests directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from unittest.mock import Mock, patch

from tests.production.base_test_jira_utils_command import TestJiraUtilsCommand


class TestTestFixtureReset(TestJiraUtilsCommand):

    # =============================================================================
    # PUBLIC TEST METHODS (sorted alphabetically)
    # =============================================================================

    @patch('testfixture_cli.handlers.JiraInstanceManager')
    def test_reset_operation_handles_issues_to_reset(self, mock_jira_class):
        # Given: Issues that need to be reset for rule testing
        mock_jira_instance = self._create_scenario_with_issues_needing_reset_from_spec(mock_jira_class, [
            {'key': 'PROJ-1', 'current': 'In Progress', 'reset_to': 'To Do'},
            {'key': 'PROJ-2', 'current': 'Done',        'reset_to': 'In Progress', 'context': 'Bug fix'}
        ])
        
        # When: Reset operation is executed
        self._execute_reset_operation("test-set-label")
        
        # Then: Both issues should be found and reset to starting status
        mock_jira_instance.get_issues_by_label.assert_called_once_with("test-set-label")
        assert mock_jira_instance.update_issue_status.call_count == 2
        mock_jira_instance.update_issue_status.assert_any_call('PROJ-1', 'To Do')
        mock_jira_instance.update_issue_status.assert_any_call('PROJ-2', 'In Progress')

    @patch('testfixture_cli.handlers.JiraInstanceManager')
    def test_reset_operation_handles_jira_connection_failure(self, mock_jira_class):
        # Given: Jira connection failure scenario
        mock_jira_instance = Mock()
        mock_jira_instance.connect.return_value = False  # Connection fails
        mock_jira_instance.get_issues_by_label.return_value = []
        mock_jira_instance.update_issue_status.return_value = False
        mock_jira_class.return_value = mock_jira_instance
        
        # When: Reset operation is executed
        self._execute_reset_operation()
        
        # Then: Should handle connection failure gracefully
        # Connection failure means get_issues_by_label might not be called
        mock_jira_instance.connect.assert_called()

    @patch('testfixture_cli.handlers.JiraInstanceManager')
    def test_reset_operation_handles_no_issues_found(self, mock_jira_class):
        # Given: Mock Jira instance that returns no issues
        mock_jira_instance = self._create_scenario_with_issues_needing_reset_from_spec(mock_jira_class, [])
        
        # When: Reset operation is executed
        self._execute_reset_operation()
        
        # Then: Should handle empty scenario gracefully
        mock_jira_instance.update_issue_status.assert_not_called()

    @patch('testfixture_cli.handlers.JiraInstanceManager')
    def test_reset_operation_skips_issues_already_in_starting_status(self, mock_jira_class):
        # Given: Issues already in starting status
        mock_jira_instance = self._create_scenario_with_issues_needing_reset_from_spec(mock_jira_class, [
            {'key': 'PROJ-3', 'current': 'To Do', 'reset_to': 'To Do'}
        ])
        
        # When: Reset operation is executed
        self._execute_reset_operation()
        
        # Then: Should skip issues already in starting status
        mock_jira_instance.update_issue_status.assert_not_called()

    @patch('testfixture_cli.handlers.JiraInstanceManager')
    def test_reset_operation_with_force_update(self, mock_jira_class):
        # Given: Mock Jira manager with test issue that would normally be skipped
        mock_jira_instance = self._create_scenario_with_issues_needing_reset_from_spec(mock_jira_class, [
            {'key': 'PROJ-1', 'current': 'To Do', 'reset_to': 'To Do'}
        ])
        
        # When: Reset operation is executed with force update
        self._execute_reset_operation_with_force_update()
        
        # Then: Verify the actual Jira API calls
        assert mock_jira_instance.update_issue_status.call_count == 2
        mock_jira_instance.update_issue_status.assert_any_call('PROJ-1', 'Done')   # First transition: To Do → Done
        mock_jira_instance.update_issue_status.assert_any_call('PROJ-1', 'To Do')  # Second transition: Done → To Do

    # =============================================================================
    # PRIVATE HELPER METHODS (sorted alphabetically)
    # =============================================================================


    def _create_scenario_with_issues_needing_reset_from_spec(self, mock_jira_class, issue_specs):
        issue_data_list = []
        
        for i, spec in enumerate(issue_specs):
            context_prefix = f"{spec.get('context', '')} - " if spec.get('context') else ""
            if i == 0:
                summary = f"{context_prefix}I was in {spec['reset_to']} - expected to be in Done"
            else:
                summary = f"{context_prefix}starting in {spec['reset_to']} - expected to be in Done"
            
            issue_data = {
                'key': spec['key'],
                'summary': summary,
                'status': spec['current']
            }
            issue_data_list.append(issue_data)
        
        mock_jira_instance = Mock()
        mock_jira_instance.get_issues_by_label.return_value = issue_data_list
        mock_jira_instance.update_issue_status.return_value = True
        mock_jira_instance.connect.return_value = True
        mock_jira_class.return_value = mock_jira_instance
        return mock_jira_instance

    def _execute_reset_operation(self, test_set_label="test-set-label"):
        self._execute_JiraUtil_with_args('tf', 'r', '--tsl', test_set_label)

    def _execute_reset_operation_with_force_update(self, test_set_label="test-set-label", force_update_via="Done"):
        self._execute_JiraUtil_with_args('tf', 'r', '--tsl', test_set_label, '--force-update-via', force_update_via)


if __name__ == "__main__":
    pytest.main([__file__])