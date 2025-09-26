"""
Tests for test fixture commands.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from testfixture.workflow import run_TestFixture_Reset, run_assert_expectations
from testfixture.issue_processor import process_issues_by_label, assert_issues_expectations
from jira_manager import JiraInstanceManager
from .fixtures.test_fixture_scenarios import (
    create_reset_scenario_with_expectations,
    create_assert_scenario_with_expectations,
    create_empty_scenario_with_expectations,
    create_connection_failure_scenario_with_expectations,
    create_skip_scenario_with_expectations
)
from .fixtures.base_fixtures import create_mock_manager_with_expected_results, create_reset_result, create_assert_result, TEST_FIXTURE_ISSUES


class TestTestFixtureAPI:
    """Test the test fixture functionality for verifying Jira automation rules."""
    
    def test_reset_operation_prepares_issues_for_rule_testing(self):
        """Test that reset operation changes issue status to starting state for rule verification."""
        # Given: Test scenario with issues that need reset and expected results
        scenario_with_issues_needing_reset = create_reset_scenario_with_expectations()
        
        # When: User runs the reset operation using the scenario's mock manager
        reset_result = process_issues_by_label(scenario_with_issues_needing_reset, "rule-testing")
        
        # Then: Results should match the scenario's expected outcomes
        assert reset_result['success'] == scenario_with_issues_needing_reset.expected_success
        assert reset_result['processed'] == scenario_with_issues_needing_reset.expected_processed
        assert reset_result['updated'] == scenario_with_issues_needing_reset.expected_updated
        assert reset_result['skipped'] == scenario_with_issues_needing_reset.expected_skipped
        assert len(reset_result['errors']) == len(scenario_with_issues_needing_reset.expected_errors)
        
        # And: Jira manager should be called correctly
        scenario_with_issues_needing_reset.connect.assert_called_once()
        scenario_with_issues_needing_reset.get_issues_by_label.assert_called_once_with("rule-testing")
        assert scenario_with_issues_needing_reset.update_issue_status.call_count == scenario_with_issues_needing_reset.expected_updated
    
    def test_assert_operation_verifies_rule_automation_worked(self):
        """Test that assert operation checks if automation rules moved issues to expected status."""
        # Given: Test scenario with issues after automation rules have run
        scenario_with_issues_after_automation = create_assert_scenario_with_expectations()
        
        # When: User runs the assert operation using the scenario's mock manager
        assert_result = assert_issues_expectations(scenario_with_issues_after_automation, "rule-testing")
        
        # Then: Results should match the scenario's expected outcomes
        assert assert_result['success'] == scenario_with_issues_after_automation.expected_success
        assert assert_result['processed'] == scenario_with_issues_after_automation.expected_processed
        assert assert_result['passed'] == 1  # One rule worked correctly
        assert assert_result['failed'] == 1  # One rule failed
        assert assert_result['not_evaluated'] == 0
        assert len(assert_result['failures']) == 1
        assert 'PROJ-2' in assert_result['failures'][0]  # PROJ-2 rule failed
    
    def test_reset_operation_handles_no_issues_found(self):
        """Test that reset operation handles case when no test issues are found."""
        # Given: Empty scenario with expected results
        scenario_with_no_issues = create_empty_scenario_with_expectations()
        
        # When: User runs reset operation using the scenario's mock manager
        reset_result = process_issues_by_label(scenario_with_no_issues, "rule-testing")
        
        # Then: Results should match the scenario's expected outcomes
        assert reset_result['success'] == scenario_with_no_issues.expected_success
        assert reset_result['processed'] == scenario_with_no_issues.expected_processed
        assert reset_result['updated'] == scenario_with_no_issues.expected_updated
        assert reset_result['skipped'] == scenario_with_no_issues.expected_skipped
    
    def test_reset_operation_handles_jira_connection_failure(self):
        """Test that reset operation handles Jira connection failures gracefully."""
        # Given: Connection failure scenario with expected results
        scenario_with_connection_failure = create_connection_failure_scenario_with_expectations()
        
        # When: User runs reset operation using the scenario's mock manager
        reset_result = process_issues_by_label(scenario_with_connection_failure, "rule-testing")
        
        # Then: Results should match the scenario's expected outcomes
        assert reset_result['success'] == scenario_with_connection_failure.expected_success
        assert 'error' in reset_result
        assert 'Failed to connect to Jira' in reset_result['error']
    
    def test_reset_operation_skips_issues_already_in_starting_status(self):
        """Test that reset operation skips issues already in their starting status."""
        # Given: Test scenario with issue already in starting status
        scenario_with_issues_already_in_starting_status = create_skip_scenario_with_expectations()
        
        # When: User runs reset operation using the scenario's mock manager
        reset_result = process_issues_by_label(scenario_with_issues_already_in_starting_status, "rule-testing")
        
        # Then: Results should match the scenario's expected outcomes
        assert reset_result['success'] == scenario_with_issues_already_in_starting_status.expected_success
        assert reset_result['processed'] == scenario_with_issues_already_in_starting_status.expected_processed
        assert reset_result['updated'] == scenario_with_issues_already_in_starting_status.expected_updated
        assert reset_result['skipped'] == scenario_with_issues_already_in_starting_status.expected_skipped
        scenario_with_issues_already_in_starting_status.update_issue_status.assert_not_called()
    
    def test_reset_workflow_command_orchestrates_rule_testing_preparation(self):
        """Test that reset workflow command coordinates the rule testing preparation process."""
        # Given: High-level reset workflow command and mock dependencies
        with patch('testfixture.workflow.JiraInstanceManager') as mock_manager_class, \
             patch('testfixture.workflow.process_issues_by_label') as mock_process:
            
            mock_jira_manager = Mock()
            mock_manager_class.return_value = mock_jira_manager
            mock_process.return_value = create_reset_result(processed=1, updated=1)
            
            # When: User runs the reset workflow command
            with patch('builtins.print'):
                run_TestFixture_Reset(mock_jira_manager, "rule-testing")
            
            # Then: Should call reset process
            mock_process.assert_called_once_with(mock_jira_manager, "rule-testing")
        
    def test_assert_workflow_command_orchestrates_rule_verification(self):
        """Test that assert workflow command coordinates the rule verification process."""
        # Given: High-level assert workflow command and mock dependencies
        with patch('testfixture.workflow.JiraInstanceManager') as mock_manager_class, \
             patch('testfixture.workflow.assert_issues_expectations') as mock_assert:
            
            mock_jira_manager = Mock()
            mock_manager_class.return_value = mock_jira_manager
            mock_assert.return_value = create_assert_result(processed=1, passed=1)
            
            # When: User runs the assert workflow command
            with patch('builtins.print'):
                run_assert_expectations(mock_jira_manager, "rule-testing")
            
            # Then: Should call assert process
            mock_assert.assert_called_once_with(mock_jira_manager, "rule-testing")
    
    def test_trigger_operation_adds_label_when_not_present(self):
        """Test that trigger operation adds label when issue doesn't have it."""
        # Given: Issue without the trigger label
        issue_without_label = self._create_mock_issue_with_labels([])
        mock_manager = self._create_mock_jira_manager(issue_without_label)
        
        # When: Trigger operation is executed
        self._execute_trigger_operation(mock_manager)
        
        # Then: Label should be added to the issue
        self._assert_label_was_added(issue_without_label)
    
    def test_trigger_operation_removes_and_adds_label_when_present(self):
        """Test that trigger operation removes existing label then adds it back."""
        # Given: Issue with the trigger label already present
        issue_with_label = self._create_mock_issue_with_labels(["TransitionSprintItems"])
        mock_manager = self._create_mock_jira_manager(issue_with_label)
        
        # When: Trigger operation is executed
        self._execute_trigger_operation(mock_manager)
        
        # Then: Label should be removed then added back
        self._assert_label_was_removed_then_added(issue_with_label)
    
    def _create_mock_issue_with_labels(self, labels):
        """Create a mock issue with specified labels."""
        mock_issue = Mock()
        mock_issue.key = "TAPS-212"
        mock_issue.fields.labels = labels
        return mock_issue
    
    def _create_mock_jira_manager(self, mock_issue):
        """Create a mock Jira manager that returns the specified issue."""
        mock_jira_manager = Mock()
        mock_jira_manager.connect.return_value = True
        mock_jira_manager.jira.issue.return_value = mock_issue
        return mock_jira_manager
    
    def _execute_trigger_operation(self, mock_manager):
        """Execute the trigger operation with mocked dependencies."""
        from testfixture.workflow import run_trigger_operation
        with patch('builtins.print'):
            run_trigger_operation(mock_manager, "TransitionSprintItems", "TAPS-212")
    
    def _assert_label_was_added(self, mock_issue):
        """Assert that the label was added to the issue."""
        mock_issue.update.assert_called_once()
        call_args = mock_issue.update.call_args
        assert "TransitionSprintItems" in call_args[1]["fields"]["labels"]
    
    def _assert_label_was_removed_then_added(self, mock_issue):
        """Assert that the label was removed then added back."""
        assert mock_issue.update.call_count == 2  # Called twice: once to remove, once to add


if __name__ == "__main__":
    pytest.main([__file__])
