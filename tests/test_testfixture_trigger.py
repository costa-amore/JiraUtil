"""
Tests for test fixture trigger operations.
"""

import pytest
from unittest.mock import Mock, patch


class TestTestFixtureTrigger:
    """Test cases for trigger operations."""

    def test_trigger_operation_adds_label_when_not_present(self):
        # Given: Issue without the trigger label
        issue_without_label = self._create_mock_issue_with_labels([])
        mock_manager = self._create_mock_jira_manager(issue_without_label)
        
        # When: Trigger operation is executed
        self._execute_trigger_operation(mock_manager)
        
        # Then: Label should be added to the issue
        self._assert_label_was_added(issue_without_label)
    
    def test_trigger_operation_removes_and_adds_label_when_present(self):
        # Given: Issue with the trigger label already present
        issue_with_label = self._create_mock_issue_with_labels(["TransitionSprintItems"])
        mock_manager = self._create_mock_jira_manager(issue_with_label)
        
        # When: Trigger operation is executed
        self._execute_trigger_operation(mock_manager)
        
        # Then: Label should be removed then added back
        self._assert_label_was_removed_then_added(issue_with_label)
    
    def test_trigger_operation_logs_info_when_label_removed_and_added(self):
        # Given: Issue with the trigger label already present
        issue_with_label = self._create_mock_issue_with_labels(["TransitionSprintItems"])
        mock_manager = self._create_mock_jira_manager(issue_with_label)
        
        # When: Trigger operation is executed
        mock_print = self._execute_trigger_operation_with_print_capture(mock_manager)
        
        # Then: Should log INFO messages for remove and add operations
        self._assert_info_logging_for_remove_and_add(mock_print)
    
    def test_trigger_operation_logs_fatal_error_when_issue_not_found(self):
        # Given: Jira manager that raises exception when getting issue
        mock_manager = self._create_mock_jira_manager_that_fails()
        
        # When: Trigger operation is executed
        mock_print = self._execute_trigger_operation_with_print_capture(mock_manager)
        
        # Then: Should log FATAL ERROR for issue not found
        self._assert_fatal_error_logging_for_issue_not_found(mock_print)
    
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
    
    def _execute_trigger_operation(self, mock_manager):
        from testfixture.workflow import run_trigger_operation
        run_trigger_operation(mock_manager, "TransitionSprintItems", "TAPS-212")
    
    def _execute_trigger_operation_with_print_capture(self, mock_manager):
        from testfixture.workflow import run_trigger_operation
        with patch('builtins.print') as mock_print:
            try:
                run_trigger_operation(mock_manager, "TransitionSprintItems", "TAPS-212")
            except Exception:
                # Exception is expected, but we still want to capture the print output
                pass
        return mock_print
    
    def _assert_label_was_added(self, mock_issue):
        mock_issue.update.assert_called_once()
        call_args = mock_issue.update.call_args
        assert "TransitionSprintItems" in call_args[1]["fields"]["labels"]
    
    def _assert_label_was_removed_then_added(self, mock_issue):
        assert mock_issue.update.call_count == 2  # Called twice: once to remove, once to add
    
    def _create_mock_jira_manager_that_fails(self):
        mock_jira_manager = Mock()
        mock_jira_manager.connect.return_value = True
        mock_jira_manager.jira.issue.side_effect = Exception("Issue not found")
        return mock_jira_manager
    
    def _assert_info_logging_for_remove_and_add(self, mock_print):
        calls = mock_print.call_args_list
        assert len(calls) >= 2
        
        # Check for INFO messages about label operations
        info_messages = [call[0][0] for call in calls if len(call[0]) > 0]
        remove_message = any("INFO" in msg and "removed" in msg for msg in info_messages)
        add_message = any("INFO" in msg and "set" in msg for msg in info_messages)
        
        assert remove_message, f"Expected INFO message about label removal, got: {info_messages}"
        assert add_message, f"Expected INFO message about label addition, got: {info_messages}"
    
    def _assert_fatal_error_logging_for_issue_not_found(self, mock_print):
        calls = mock_print.call_args_list
        assert len(calls) >= 1
        
        # Check for FATAL ERROR message
        error_messages = [call[0][0] for call in calls if len(call[0]) > 0]
        fatal_message = any("FATAL ERROR" in msg for msg in error_messages)
        
        assert fatal_message, f"Expected FATAL ERROR message, got: {error_messages}"

    def test_trigger_operation_with_multiple_labels_adds_all_labels(self):
        # Given: Issue without any of the trigger labels
        issue_without_labels = self._create_mock_issue_with_labels([])
        mock_manager = self._create_mock_jira_manager(issue_without_labels)
        
        # When: Trigger operation is executed with multiple labels
        self._execute_trigger_operation_with_multiple_labels(mock_manager, "TransitionSprintItems,CloseEpic,UpdateStatus")
        
        # Then: All labels should be added to the issue
        self._assert_all_labels_were_added(issue_without_labels, ["TransitionSprintItems", "CloseEpic", "UpdateStatus"])
    
    def test_trigger_operation_with_multiple_labels_removes_existing_and_adds_new(self):
        # Given: Issue with some existing labels
        issue_with_existing_labels = self._create_mock_issue_with_labels(["OldLabel", "AnotherLabel"])
        mock_manager = self._create_mock_jira_manager(issue_with_existing_labels)
        
        # When: Trigger operation is executed with multiple labels
        self._execute_trigger_operation_with_multiple_labels(mock_manager, "TransitionSprintItems,CloseEpic")
        
        # Then: All labels should be replaced with the new ones
        self._assert_labels_were_replaced(issue_with_existing_labels, ["TransitionSprintItems", "CloseEpic"])
    
    def test_trigger_operation_with_multiple_labels_trims_whitespace(self):
        # Given: Issue without any labels
        issue_without_labels = self._create_mock_issue_with_labels([])
        mock_manager = self._create_mock_jira_manager(issue_without_labels)
        
        # When: Trigger operation is executed with labels containing whitespace
        self._execute_trigger_operation_with_multiple_labels(mock_manager, " TransitionSprintItems , CloseEpic , UpdateStatus ")
        
        # Then: All labels should be added with whitespace trimmed
        self._assert_all_labels_were_added(issue_without_labels, ["TransitionSprintItems", "CloseEpic", "UpdateStatus"])
    
    def test_trigger_operation_with_empty_labels_shows_error(self):
        # Given: Issue without any labels
        issue_without_labels = self._create_mock_issue_with_labels([])
        mock_manager = self._create_mock_jira_manager(issue_without_labels)
        
        # When: Trigger operation is executed with empty labels
        mock_print = self._execute_trigger_operation_with_multiple_labels_and_print_capture(mock_manager, "")
        
        # Then: Should show error message
        self._assert_error_message_for_empty_labels(mock_print)
    
    def _execute_trigger_operation_with_multiple_labels(self, mock_manager, labels_string):
        from testfixture.workflow import run_trigger_operation_with_multiple_labels
        run_trigger_operation_with_multiple_labels(mock_manager, labels_string, "TAPS-212")
    
    def _execute_trigger_operation_with_multiple_labels_and_print_capture(self, mock_manager, labels_string):
        from testfixture.workflow import run_trigger_operation_with_multiple_labels
        with patch('builtins.print') as mock_print:
            try:
                run_trigger_operation_with_multiple_labels(mock_manager, labels_string, "TAPS-212")
            except Exception:
                # Exception is expected, but we still want to capture the print output
                pass
        return mock_print
    
    def _assert_all_labels_were_added(self, mock_issue, expected_labels):
        mock_issue.update.assert_called_once()
        call_args = mock_issue.update.call_args
        actual_labels = call_args[1]["fields"]["labels"]
        for label in expected_labels:
            assert label in actual_labels, f"Expected label '{label}' to be in {actual_labels}"
    
    def _assert_labels_were_replaced(self, mock_issue, expected_labels):
        mock_issue.update.assert_called_once()
        call_args = mock_issue.update.call_args
        actual_labels = call_args[1]["fields"]["labels"]
        assert set(actual_labels) == set(expected_labels), f"Expected labels {expected_labels}, got {actual_labels}"
    
    def _assert_error_message_for_empty_labels(self, mock_print):
        calls = mock_print.call_args_list
        assert len(calls) >= 1
        
        # Check for error message about empty labels
        error_messages = [call[0][0] for call in calls if len(call[0]) > 0]
        error_message = any("error" in msg.lower() and "label" in msg.lower() for msg in error_messages)
        
        assert error_message, f"Expected error message about empty labels, got: {error_messages}"


if __name__ == "__main__":
    pytest.main([__file__])
