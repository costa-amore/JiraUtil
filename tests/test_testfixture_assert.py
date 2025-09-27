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
    create_assert_scenario_with_expectations
)


class TestTestFixtureAssert:
    """Test cases for assert operations."""

    def test_assert_operation_verifies_rule_automation_worked(self):
        # Given: Issues after automation has run
        scenario_with_issues_after_automation = create_assert_scenario_with_expectations()
        mock_jira_manager = scenario_with_issues_after_automation
        
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

    def _execute_assert_operation(self, mock_manager):
        from testfixture.workflow import run_assert_expectations
        with patch('builtins.print'):
            run_assert_expectations(mock_manager, "rule-testing")


if __name__ == "__main__":
    pytest.main([__file__])
