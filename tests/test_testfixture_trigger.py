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


    @pytest.mark.parametrize("scenario,existing_labels,trigger_labels,expected_final_labels,expected_update_calls", [
        ("adds all labels when none present", [],
         "TransitionSprintItems,CloseEpic,UpdateStatus",
         ["TransitionSprintItems", "CloseEpic", "UpdateStatus"], 1),
        
        ("adds new labels while preserving existing ones", ["OldLabel", "AnotherLabel"],
         "TransitionSprintItems,CloseEpic",
         ["OldLabel", "AnotherLabel", "TransitionSprintItems", "CloseEpic"], 1),
        
        ("trims whitespace from labels while preserving existing ones", ["ExistingLabel"],
         " TransitionSprintItems , CloseEpic , UpdateStatus ",
         ["ExistingLabel", "TransitionSprintItems", "CloseEpic", "UpdateStatus"], 1),
        
        ("single label: adds when not present", [],
         "TransitionSprintItems",
         ["TransitionSprintItems"], 1),
        
        ("single label: adds while preserving existing ones", ["OldLabel", "AnotherLabel"],
         "TransitionSprintItems",
         ["OldLabel", "AnotherLabel", "TransitionSprintItems"], 1),
    ])
    def test_trigger_scenarios_add_only(self, scenario, existing_labels, trigger_labels, expected_final_labels, expected_update_calls):
        """Test trigger scenarios where no labels need removing - just add them."""
        # Given: Issue with specific existing labels
        issue = self._create_mock_issue_with_labels(existing_labels)
        mock_manager = self._create_mock_jira_manager(issue)

        # When: Trigger operation is executed
        with patch('builtins.print') as mock_print:
            run_trigger_operation(mock_manager, "TAPS-211", trigger_labels)

        # Then: Should call update the expected number of times
        assert issue.update.call_count == expected_update_calls, f"Expected {expected_update_calls} updates for scenario: {scenario}"
        
        # Verify the final labels match expectations
        final_call = issue.update.call_args_list[-1]
        actual_labels = final_call[1]["fields"]["labels"]
        assert set(actual_labels) == set(expected_final_labels), f"Expected {expected_final_labels}, got {actual_labels} for scenario: {scenario}"
        
        # Verify logging: should log add message only, no remove message
        remove_message, add_message = self._extract_messages(mock_print)
        assert not remove_message, f"Expected no INFO message about label removal for scenario: {scenario}"
        assert add_message, f"Expected INFO message about label addition for scenario: {scenario}"

    @pytest.mark.parametrize("scenario,existing_labels,trigger_labels,expected_after_removal,expected_final_labels", [
        ("single label: removes and adds when present", ["TransitionSprintItems"],
         "TransitionSprintItems",
         [], ["TransitionSprintItems"]),

        ("single label: removes and adds while preserving existing ones", ["TransitionSprintItems", "OldLabel"],
         "TransitionSprintItems",
         ["OldLabel"], ["TransitionSprintItems", "OldLabel"]),

        ("multiple labels: removes existing trigger labels then adds all", ["OldLabel", "Trigger-Epic-Transition-rules"],
         "Trigger-SBI-Transition-rules,Trigger-Epic-Transition-rules",
         ["OldLabel"], ["OldLabel", "Trigger-SBI-Transition-rules", "Trigger-Epic-Transition-rules"]),

        ("multiple labels: removes all existing trigger labels then adds all", ["OldLabel", "Trigger-SBI-Transition-rules", "Trigger-Epic-Transition-rules"],
         "Trigger-SBI-Transition-rules,Trigger-Epic-Transition-rules",
         ["OldLabel"], ["OldLabel", "Trigger-SBI-Transition-rules", "Trigger-Epic-Transition-rules"]),

        ("single label: removes and adds when present (no other labels)", ["TransitionSprintItems"],
         "TransitionSprintItems",
         [], ["TransitionSprintItems"]),

        ("multiple labels: preserves existing labels when all trigger labels already present", ["TransitionSprintItems", "CloseEpic", "UpdateStatus", "ExistingLabel"],
         "TransitionSprintItems,CloseEpic,UpdateStatus",
         ["ExistingLabel"], ["TransitionSprintItems", "CloseEpic", "UpdateStatus", "ExistingLabel"]),

        ("multiple labels: adds missing labels while preserving existing ones", ["TransitionSprintItems", "OldLabel"],
         "TransitionSprintItems,CloseEpic,UpdateStatus",
         ["OldLabel"], ["TransitionSprintItems", "OldLabel", "CloseEpic", "UpdateStatus"]),
    ])
    def test_trigger_scenarios_remove_and_add(self, scenario, existing_labels, trigger_labels, expected_after_removal, expected_final_labels):
        """Test trigger scenarios where labels need removing first, then adding."""
        # Given: Issue with specific existing labels
        issue = self._create_mock_issue_with_labels(existing_labels)
        mock_manager = self._create_mock_jira_manager(issue)
        
        # When: Trigger operation is executed
        with patch('builtins.print') as mock_print:
            run_trigger_operation(mock_manager, "TAPS-211", trigger_labels)
        
        # Then: Should call update exactly once (just add all labels)
        assert issue.update.call_count == 1, f"Expected 1 update for scenario: {scenario}"
        
        # Verify the final labels match expectations
        final_call = issue.update.call_args_list[0]
        actual_final_labels = final_call[1]["fields"]["labels"]
        assert set(actual_final_labels) == set(expected_final_labels), f"Expected {expected_final_labels}, got {actual_final_labels} for scenario: {scenario}"
        
        # Verify logging: should log both remove and add messages
        remove_message, add_message = self._extract_messages(mock_print)
        assert remove_message, f"Expected INFO message about label removal for scenario: {scenario}"
        assert add_message, f"Expected INFO message about label addition for scenario: {scenario}"

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
        messages = [call[0][0] for call in calls if len(call[0]) > 0]
        remove_message = any("Labels Removed:" in msg for msg in messages)
        add_message = any("Labels Set:" in msg for msg in messages)
        return remove_message, add_message
    


if __name__ == "__main__":
    pytest.main([__file__])
