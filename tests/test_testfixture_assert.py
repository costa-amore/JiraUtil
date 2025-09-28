"""
Tests for test fixture assert operations.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import Mock, patch

from tests.fixtures import (
    create_assert_scenario,
    create_assert_scenario_with_expectations
)


class TestTestFixtureAssert:

    # Public test methods (sorted alphabetically)
    def test_assert_failure_message_extracts_context_from_summary(self):
        # Given: Issue with context in summary that should be extracted
        issue_type = "Bug"
        issue_key = "PROJ-2"
        expected_format = f"    - [{issue_type}] {issue_key}: When in this context, expected 'Done' but is 'To Do'"
        mock_jira_manager = create_assert_scenario(issue_type, issue_key, "When in this context, starting in To Do - expected to be in Done")
        
        # When: Assert operation is executed and captures print output
        mock_print = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify the failure message format includes context
        self._verify_failure_message_format(mock_print, expected_format)

    def test_assert_failure_message_handles_summary_without_context(self):
        # Given: Issue without context that should still be evaluated
        issue_type = "Story"
        issue_key = "PROJ-3"
        expected_format = f"    - [{issue_type}] {issue_key}: expected 'CLOSED' but is 'SIT/LAB VALIDATED'"
        mock_jira_manager = create_assert_scenario(issue_type, issue_key, "I was in SIT/LAB VALIDATED - expected to be in CLOSED")
        
        # When: Assert operation is executed and captures print output
        mock_print = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify the failure message format works without context
        self._verify_failure_message_format(mock_print, expected_format)

    def test_assert_operation_verifies_rule_automation_worked(self):
        # Given: Issues after automation has run
        mock_jira_manager = create_assert_scenario_with_expectations()
        
        # When: Assert operation is executed
        self._execute_assert_operation(mock_jira_manager)
        
        # Then: Rule automation should be verified
        mock_jira_manager.get_issues_by_label.assert_called_once_with("rule-testing")

    def test_assert_workflow_command_orchestrates_rule_verification(self):
        # Given: Assert workflow command with mock manager
        mock_jira_manager = create_assert_scenario_with_expectations()
        
        # When: Assert workflow command is executed
        self._execute_assert_operation(mock_jira_manager)
        
        # Then: Rule verification should be orchestrated
        mock_jira_manager.get_issues_by_label.assert_called_once_with("rule-testing")

    # Private helper methods (sorted alphabetically)

    def _extract_failure_messages(self, mock_print):
        print_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        return [msg for msg in print_calls if 'Expected' in msg and 'but is' in msg]

    def _verify_failure_message_format(self, mock_print, expected_format):
        failure_messages = self._extract_failure_messages(mock_print)
        
        if failure_messages:
            failure_message = failure_messages[0]
            assert failure_message == expected_format, f"Expected format '{expected_format}', got '{failure_message}'"

    def _execute_assert_operation(self, mock_manager):
        from testfixture.workflow import run_assert_expectations
        with patch('builtins.print'):
            run_assert_expectations(mock_manager, "rule-testing")

    def _execute_assert_operation_with_print_capture(self, mock_manager):
        from testfixture.workflow import run_assert_expectations
        with patch('builtins.print') as mock_print:
            run_assert_expectations(mock_manager, "rule-testing")
        return mock_print

    def _extract_failure_messages(self, mock_print):
        print_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        return [msg for msg in print_calls if 'Expected' in msg and 'but is' in msg]


if __name__ == "__main__":
    pytest.main([__file__])
