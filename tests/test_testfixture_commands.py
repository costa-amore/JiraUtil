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
        reset_scenario = create_reset_scenario_with_expectations()
        
        # When: User runs the reset operation to prepare issues for testing
        result = process_issues_by_label(reset_scenario, "rule-testing")
        
        # Then: Results should match the expected scenario
        assert result['success'] == reset_scenario.expected_success
        assert result['processed'] == reset_scenario.expected_processed
        assert result['updated'] == reset_scenario.expected_updated
        assert result['skipped'] == reset_scenario.expected_skipped
        assert len(result['errors']) == len(reset_scenario.expected_errors)
        
        # And: Jira manager should be called correctly
        reset_scenario.connect.assert_called_once()
        reset_scenario.get_issues_by_label.assert_called_once_with("rule-testing")
        assert reset_scenario.update_issue_status.call_count == reset_scenario.expected_updated
    
    def test_assert_operation_verifies_rule_automation_worked(self):
        """Test that assert operation checks if automation rules moved issues to expected status."""
        # Given: Test scenario with issues after automation rules have run
        # One issue should be in correct status (rule worked), one should not (rule failed)
        assert_scenario = create_assert_scenario_with_expectations()
        
        # When: User runs the assert operation to verify rule automation worked
        result = assert_issues_expectations(assert_scenario, "rule-testing")
        
        # Then: Results should match the expected scenario
        assert result['success'] == assert_scenario.expected_success
        assert result['processed'] == assert_scenario.expected_processed
        # Note: Assert operation has different result structure (passed/failed vs updated/skipped)
        assert result['passed'] == 1  # One rule worked correctly
        assert result['failed'] == 1  # One rule failed
        assert result['not_evaluated'] == 0
        assert len(result['failures']) == 1
        assert 'PROJ-2' in result['failures'][0]  # PROJ-2 rule failed
    
    def test_reset_operation_handles_no_issues_found(self):
        """Test that reset operation handles case when no test issues are found."""
        # Given: Empty scenario with expected results
        empty_scenario = create_empty_scenario_with_expectations()
        
        # When: User runs reset operation
        result = process_issues_by_label(empty_scenario, "rule-testing")
        
        # Then: Results should match the expected scenario
        assert result['success'] == empty_scenario.expected_success
        assert result['processed'] == empty_scenario.expected_processed
        assert result['updated'] == empty_scenario.expected_updated
        assert result['skipped'] == empty_scenario.expected_skipped
    
    def test_reset_operation_handles_jira_connection_failure(self):
        """Test that reset operation handles Jira connection failures gracefully."""
        # Given: Connection failure scenario with expected results
        connection_failure_scenario = create_connection_failure_scenario_with_expectations()
        
        # When: User runs reset operation
        result = process_issues_by_label(connection_failure_scenario, "rule-testing")
        
        # Then: Results should match the expected scenario
        assert result['success'] == connection_failure_scenario.expected_success
        assert 'error' in result
        assert 'Failed to connect to Jira' in result['error']
    
    def test_reset_operation_skips_issues_already_in_starting_status(self):
        """Test that reset operation skips issues already in their starting status."""
        # Given: Test scenario with issue already in starting status
        skip_scenario = create_skip_scenario_with_expectations()
        
        # When: User runs reset operation
        result = process_issues_by_label(skip_scenario, "rule-testing")
        
        # Then: Results should match the expected scenario
        assert result['success'] == skip_scenario.expected_success
        assert result['processed'] == skip_scenario.expected_processed
        assert result['updated'] == skip_scenario.expected_updated
        assert result['skipped'] == skip_scenario.expected_skipped
        skip_scenario.update_issue_status.assert_not_called()
    
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
                run_TestFixture_Reset("https://jira.example.com", "user", "pass", "rule-testing")
            
            # Then: Should create Jira manager and call reset process
            mock_manager_class.assert_called_once_with("https://jira.example.com", "user", "pass")
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
                run_assert_expectations("https://jira.example.com", "user", "pass", "rule-testing")
            
            # Then: Should create Jira manager and call assert process
            mock_manager_class.assert_called_once_with("https://jira.example.com", "user", "pass")
            mock_assert.assert_called_once_with(mock_jira_manager, "rule-testing")


if __name__ == "__main__":
    pytest.main([__file__])
