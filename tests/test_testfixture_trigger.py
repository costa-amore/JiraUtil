"""
Tests for test fixture trigger operations.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import Mock, patch
from testfixture.trigger_processor import _parse_labels_string


class TestTestFixtureTrigger:

    # Public test methods 
    @pytest.mark.parametrize("scenario,trigger_labels,expected_error_contains,mock_manager_factory", [
        ("shows error for empty labels", "", ["fatal", "error"], "normal"),
        ("shows error for whitespace-only labels", "   ", ["fatal", "error"], "normal"),
        ("logs fatal error when issue not found", "TransitionSprintItems", ["fatal", "error"], "fails"),
    ])
    @patch('testfixture_cli.handlers.JiraInstanceManager')
    def test_trigger_error_scenarios(self, mock_jira_class, scenario, trigger_labels, expected_error_contains, mock_manager_factory):
        # Given: Mock Jira manager based on scenario
        mock_jira_instance = self._create_mock_jira_instance_for_scenario(mock_manager_factory)
        mock_jira_class.return_value = mock_jira_instance
        
        # When: CLI trigger command is executed
        mock_print = self._execute_cli_command_with_trigger(['tf', 't', '--tl', trigger_labels], 'PROJ-1')
        
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
    @patch('testfixture_cli.handlers.JiraInstanceManager')
    @patch('time.sleep')  # Mock sleep to avoid 5-second delay when trigger labels overlap with existing labels
    def test_trigger_operation_cli_scenarios(self, mock_sleep, mock_jira_class, scenario, existing_labels, trigger_labels, expected_final_labels, expected_update_calls):
        # Given: Mock Jira manager with test issue
        issue_data = {
            'key': 'PROJ-1',
            'summary': 'Test issue for trigger operation',
            'status': 'To Do',
            'labels': existing_labels
        }
        mock_jira_instance = self._create_mock_jira_instance_with_issue(issue_data)
        mock_jira_class.return_value = mock_jira_instance
        
        # When: CLI command is executed with trigger-labels
        self._execute_cli_command_with_trigger(['tf', 't', '--tl', trigger_labels], 'PROJ-1')
        
        # Then: Verify the actual Jira API calls with properly parsed labels
        mock_jira_instance.jira.issue.assert_called_once_with('PROJ-1')
        assert mock_jira_instance.jira.issue.return_value.update.call_count == expected_update_calls
        
        # Verify the final labels are correctly parsed
        final_call = mock_jira_instance.jira.issue.return_value.update.call_args_list[-1]
        actual_labels = final_call[1]['fields']['labels']
        assert set(actual_labels) == set(expected_final_labels), f"Expected {expected_final_labels}, got {actual_labels} for scenario: {scenario}"

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
    @patch('testfixture_cli.handlers.JiraInstanceManager')
    @patch('time.sleep')  # Mock sleep to avoid 5-second delay when trigger labels overlap with existing labels
    def test_trigger_scenarios_remove_and_add(self, mock_sleep, mock_jira_class, scenario, existing_labels, trigger_labels, expected_after_removal, expected_final_labels):
        """Test trigger scenarios where labels need removing first, then adding."""
        # Given: Mock Jira instance with issue having specific existing labels
        issue_data = {
            'key': 'TAPS-211',
            'summary': 'Test issue for trigger operation',
            'status': 'To Do',
            'labels': existing_labels
        }
        mock_jira_instance = self._create_mock_jira_instance_with_issue(issue_data)
        mock_jira_class.return_value = mock_jira_instance
        
        # When: CLI trigger command is executed
        mock_print = self._execute_cli_command_with_trigger(['tf', 't', '--tl', trigger_labels], 'TAPS-211')
        
        # Then: Should call update twice when labels need removing (remove + add), once when just adding
        expected_calls = 2 if any(label in existing_labels for label in _parse_labels_string(trigger_labels)) else 1
        assert mock_jira_instance.jira.issue.return_value.update.call_count == expected_calls, f"Expected {expected_calls} update calls for scenario: {scenario}"
        
        # Verify the final labels match expectations (check the last call)
        final_call = mock_jira_instance.jira.issue.return_value.update.call_args_list[-1]
        actual_final_labels = final_call[1]["fields"]["labels"]
        assert set(actual_final_labels) == set(expected_final_labels), f"Expected {expected_final_labels}, got {actual_final_labels} for scenario: {scenario}"
        
        # Verify logging: should log both remove and add messages
        remove_message, add_message = self._extract_messages(mock_print)
        assert remove_message, f"Expected INFO message about label removal for scenario: {scenario}"
        assert add_message, f"Expected INFO message about label addition for scenario: {scenario}"


    # Private helper methods 
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

    def _create_mock_jira_instance_for_scenario(self, mock_manager_factory):
        """Create a mock Jira instance for CLI testing based on scenario."""
        if mock_manager_factory == "fails":
            mock_jira_instance = Mock()
            mock_jira_instance.jira.issue.side_effect = Exception("Issue not found")
            return mock_jira_instance
        else:
            issue_data = {
                'key': 'PROJ-1',
                'summary': 'Test issue for trigger operation',
                'status': 'To Do',
                'labels': []
            }
            return self._create_mock_jira_instance_with_issue(issue_data)


    def _create_mock_jira_instance_with_issue(self, issue_data):
        """Create a mock Jira instance with a specific issue for CLI testing."""
        mock_jira_instance = Mock()
        mock_issue = Mock()
        mock_issue.key = issue_data['key']
        mock_issue.fields.summary = issue_data['summary']
        mock_issue.fields.labels = issue_data.get('labels', [])
        mock_issue.update = Mock()
        mock_jira_instance.jira.issue.return_value = mock_issue
        return mock_jira_instance

    def _create_mock_jira_manager_that_fails(self):
        mock_jira_manager = Mock()
        mock_jira_manager.connect.return_value = True
        mock_jira_manager.jira.issue.side_effect = Exception("Issue not found")
        return mock_jira_manager

    def _execute_cli_command_with_trigger(self, command_args, issue_key):
        """Execute a CLI trigger command for testing."""
        from cli.parser import build_parser
        from testfixture_cli.handlers import handle_test_fixture_commands
        import sys
        from io import StringIO
        
        parser = build_parser()
        full_args = command_args + ['-k', issue_key]
        args = parser.parse_args(full_args)
        
        with patch('builtins.print') as mock_print:
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                with patch('sys.exit') as mock_exit:
                    try:
                        handle_test_fixture_commands(args, {})
                    except SystemExit:
                        # SystemExit is expected for error scenarios, but we still want to capture the print output
                        pass
                    # Capture stderr content as print calls for error extraction
                    stderr_content = mock_stderr.getvalue()
                    if stderr_content:
                        mock_print(stderr_content)
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
