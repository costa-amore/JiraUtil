"""
Tests for test fixture reset operations.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import Mock, patch

from tests.fixtures import (
    create_reset_scenario_with_expectations,
    create_empty_scenario_with_expectations,
    create_connection_failure_scenario_with_expectations,
    create_skip_scenario_with_expectations
)


class TestTestFixtureReset:
    """Test cases for reset operations."""

    def test_reset_operation_prepares_issues_for_rule_testing(self):
        # Given: Issues that need to be reset for rule testing
        scenario_with_issues_needing_reset = create_reset_scenario_with_expectations()
        mock_jira_manager = scenario_with_issues_needing_reset
        
        # When: Reset operation is executed
        self._execute_reset_operation(mock_jira_manager)
        
        # Then: Issues should be prepared for rule testing
        mock_jira_manager.get_issues_by_label.assert_called_once_with("rule-testing")
        mock_jira_manager.update_issue_status.assert_called()

    def test_reset_operation_handles_no_issues_found(self):
        # Given: No issues found for the label
        scenario_with_no_issues = create_empty_scenario_with_expectations()
        mock_jira_manager = scenario_with_no_issues
        
        # When: Reset operation is executed
        self._execute_reset_operation(mock_jira_manager)
        
        # Then: Should handle empty scenario gracefully
        mock_jira_manager.get_issues_by_label.assert_called_once_with("rule-testing")
        mock_jira_manager.update_issue_status.assert_not_called()

    def test_reset_operation_handles_jira_connection_failure(self):
        # Given: Jira connection failure scenario
        scenario_with_connection_failure = create_connection_failure_scenario_with_expectations()
        mock_jira_manager = scenario_with_connection_failure
        
        # When: Reset operation is executed
        self._execute_reset_operation(mock_jira_manager)
        
        # Then: Should handle connection failure gracefully
        # Connection failure means get_issues_by_label might not be called
        mock_jira_manager.connect.assert_called()

    def test_reset_operation_skips_issues_already_in_starting_status(self):
        # Given: Issues already in starting status
        scenario_with_issues_already_in_starting_status = create_skip_scenario_with_expectations()
        mock_jira_manager = scenario_with_issues_already_in_starting_status
        
        # When: Reset operation is executed
        self._execute_reset_operation(mock_jira_manager)
        
        # Then: Should skip issues already in starting status
        mock_jira_manager.get_issues_by_label.assert_called_once_with("rule-testing")
        mock_jira_manager.update_issue_status.assert_not_called()

    def test_reset_workflow_command_orchestrates_rule_testing_preparation(self):
        # Given: Reset workflow command with mock manager
        mock_jira_manager = create_reset_scenario_with_expectations()
        
        # When: Reset workflow command is executed
        self._execute_reset_operation(mock_jira_manager)
        
        # Then: Rule testing preparation should be orchestrated
        mock_jira_manager.get_issues_by_label.assert_called_once_with("rule-testing")
        mock_jira_manager.update_issue_status.assert_called()

    def _execute_reset_operation(self, mock_manager):
        from testfixture.workflow import run_TestFixture_Reset
        with patch('builtins.print'):
            run_TestFixture_Reset(mock_manager, "rule-testing")


if __name__ == "__main__":
    pytest.main([__file__])
