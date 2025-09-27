"""
Tests for test fixture trigger operations.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import Mock, patch
from testfixture.workflow import run_trigger_operation


class TestTestFixtureTrigger:

    # Public test methods (sorted alphabetically)
    @pytest.mark.parametrize("scenario,trigger_labels,expected_error_contains,mock_manager_factory", [
        ("shows error for empty labels", "", ["fatal", "error"], "normal"),
        ("shows error for whitespace-only labels", "   ", ["fatal", "error"], "normal"),
        ("logs fatal error when issue not found", "TransitionSprintItems", ["fatal", "error"], "fails"),
    ])
    def test_trigger_error_scenarios(self, scenario, trigger_labels, expected_error_contains, mock_manager_factory):
        # Given: Mock manager based on scenario
        mock_manager = self._create_mock_jira_manager_for_scenario(mock_manager_factory)
        
        # When: Trigger operation is executed
        mock_print = self._execute_trigger_operation_with_print_capture(mock_manager, trigger_labels)
        
        # Then: Should show appropriate error message
        error_found = self._extract_error_message(mock_print, expected_error_contains)
        assert error_found, f"Expected error message containing {expected_error_contains} for scenario: {scenario}"

    def test_trigger_operation_logs_info_when_label_added(self):
        # Given: Issue with no labels
        issue_with_label = self._create_mock_issue_with_labels([])
        mock_manager = self._create_mock_jira_manager(issue_with_label)
        
        # When: Trigger operation is executed
        mock_print = self._execute_trigger_operation_with_print_capture(mock_manager, "TransitionSprintItems")
        
        # Then: Should log INFO message for add operation only
        remove_message, add_message = self._extract_messages(mock_print)
        assert not remove_message, f"Expected no INFO message about label removal"
        assert add_message, f"Expected INFO message about label addition"

    def test_trigger_operation_logs_info_when_label_removed_and_added(self):
        # Given: Issue with the trigger label already present
        issue_with_label = self._create_mock_issue_with_labels(["TransitionSprintItems"])
        mock_manager = self._create_mock_jira_manager(issue_with_label)
        
        # When: Trigger operation is executed
        mock_print = self._execute_trigger_operation_with_print_capture(mock_manager, "TransitionSprintItems")
        
        # Then: Should log INFO messages for remove and add operations
        remove_message, add_message = self._extract_messages(mock_print)
        assert remove_message, f"Expected INFO message about label removal"
        assert add_message, f"Expected INFO message about label addition"

    @pytest.mark.parametrize("scenario,existing_labels,trigger_labels,expected_final_labels,expected_updates", [
        ("adds all labels when none present", [],
         "TransitionSprintItems,CloseEpic,UpdateStatus",
         ["TransitionSprintItems", "CloseEpic", "UpdateStatus"], 1),
        
        ("adds new labels while preserving existing ones", ["OldLabel", "AnotherLabel"],
         "TransitionSprintItems,CloseEpic",
         ["OldLabel", "AnotherLabel", "TransitionSprintItems", "CloseEpic"], 1),
        
        ("preserves existing labels when all trigger labels already present", ["TransitionSprintItems", "CloseEpic", "UpdateStatus", "ExistingLabel"],
         "TransitionSprintItems,CloseEpic,UpdateStatus",
         ["TransitionSprintItems", "CloseEpic", "UpdateStatus", "ExistingLabel"], 1),
        
        ("adds missing labels while preserving existing ones", ["TransitionSprintItems", "OldLabel"],
         "TransitionSprintItems,CloseEpic,UpdateStatus",
         ["TransitionSprintItems", "OldLabel", "CloseEpic", "UpdateStatus"], 1),
        
        ("trims whitespace from labels while preserving existing ones", ["ExistingLabel"],
         " TransitionSprintItems , CloseEpic , UpdateStatus ",
         ["ExistingLabel", "TransitionSprintItems", "CloseEpic", "UpdateStatus"], 1),
        
        ("single label: adds when not present", [],
         "TransitionSprintItems",
         ["TransitionSprintItems"], 1),
        
        ("single label: removes and adds when present", ["TransitionSprintItems"],
         "TransitionSprintItems",
         ["TransitionSprintItems"], 2),
        
        ("single label: adds while preserving existing ones", ["OldLabel", "AnotherLabel"],
         "TransitionSprintItems",
         ["OldLabel", "AnotherLabel", "TransitionSprintItems"], 1),
        
        ("single label: removes and adds while preserving existing ones", ["TransitionSprintItems", "OldLabel"],
         "TransitionSprintItems",
         ["TransitionSprintItems", "OldLabel"], 2),
    ])
    def test_trigger_scenarios(self, scenario, existing_labels, trigger_labels, expected_final_labels, expected_updates):
        # Given: Issue with specific existing labels
        issue = self._create_mock_issue_with_labels(existing_labels)
        mock_manager = self._create_mock_jira_manager(issue)
        
        # When: Trigger operation is executed
        run_trigger_operation(mock_manager, "TAPS-212", trigger_labels)
        
        # Then: Should call update the expected number of times
        assert issue.update.call_count == expected_updates, f"Expected {expected_updates} updates for scenario: {scenario}"
        
        # Verify the final labels match expectations
        final_call = issue.update.call_args_list[-1]
        actual_labels = final_call[1]["fields"]["labels"]
        assert set(actual_labels) == set(expected_final_labels), f"Expected {expected_final_labels}, got {actual_labels} for scenario: {scenario}"

    # Private helper methods (sorted alphabetically)
    def _create_mock_issue_with_labels(self, labels):
        mock_issue = Mock()
        mock_issue.key = "TAPS-212"
        mock_issue.fields.labels = labels
        return mock_issue

    def _create_mock_jira_manager(self, mock_issue):
        mock_jira_manager = Mock()
        mock_jira_manager.connect.return_value = True
        mock_jira_manager.jira.issue.return_value = mock_issue
        return mock_jira_manager

    def _create_mock_jira_manager_for_scenario(self, mock_manager_factory):
        if mock_manager_factory == "fails":
            return self._create_mock_jira_manager_that_fails()
        else:
            issue = self._create_mock_issue_with_labels([])
            return self._create_mock_jira_manager(issue)

    def _create_mock_jira_manager_that_fails(self):
        mock_jira_manager = Mock()
        mock_jira_manager.connect.return_value = True
        mock_jira_manager.jira.issue.side_effect = Exception("Issue not found")
        return mock_jira_manager

    def _execute_trigger_operation_with_print_capture(self, mock_manager, labels_string):
        with patch('builtins.print') as mock_print:
            try:
                run_trigger_operation(mock_manager, "TAPS-212", labels_string)
            except Exception:
                # Exception is expected, but we still want to capture the print output
                pass
        return mock_print

    def _extract_error_message(self, mock_print, expected_error_contains):
        calls = mock_print.call_args_list
        error_messages = [call[0][0] for call in calls if len(call[0]) > 0]
        return any(all(keyword in msg.lower() for keyword in expected_error_contains) for msg in error_messages)

    def _extract_messages(self, mock_print):
        calls = mock_print.call_args_list
        info_messages = [call[0][0] for call in calls if len(call[0]) > 0]
        remove_message = any("INFO" in msg and "Removed" in msg for msg in info_messages)
        add_message = any("INFO" in msg and "Set" in msg for msg in info_messages)
        return remove_message, add_message
    


if __name__ == "__main__":
    pytest.main([__file__])
