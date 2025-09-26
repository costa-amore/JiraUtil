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


if __name__ == "__main__":
    pytest.main([__file__])
