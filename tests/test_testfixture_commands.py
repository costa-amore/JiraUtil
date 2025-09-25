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
from .fixtures import TEST_FIXTURE_ISSUES, TEST_FIXTURE_ASSERT_ISSUES, create_mock_manager, create_reset_result, create_assert_result


class TestTestFixtureAPI:
    
    def test_user_can_reset_test_fixtures(self):
        """Test that users can reset test fixtures through the API."""
        mock_manager = create_mock_manager(issues=TEST_FIXTURE_ISSUES[:2])
        
        result = process_issues_by_label(mock_manager, "rule-testing")
        assert result['success'] is True
        assert result['processed'] == 2
        assert result['updated'] == 2
        assert result['skipped'] == 0
        assert len(result['errors']) == 0
        
        mock_manager.connect.assert_called_once()
        mock_manager.get_issues_by_label.assert_called_once_with("rule-testing")
        assert mock_manager.update_issue_status.call_count == 2
    
    def test_user_can_assert_test_fixtures(self):
        """Test that users can assert test fixtures through the API."""
        mock_manager = create_mock_manager(issues=TEST_FIXTURE_ASSERT_ISSUES)
        
        result = assert_issues_expectations(mock_manager, "rule-testing")
        assert result['success'] is True
        assert result['processed'] == 2
        assert result['passed'] == 1
        assert result['failed'] == 1
        assert result['not_evaluated'] == 0
        assert len(result['failures']) == 1
        assert 'PROJ-2' in result['failures'][0]
    
    def test_user_gets_appropriate_feedback_for_edge_cases(self):
        """Test that users get appropriate feedback for edge cases."""
        mock_manager = create_mock_manager(issues=[])
        
        result = process_issues_by_label(mock_manager, "rule-testing")
        assert result['success'] is True
        assert result['processed'] == 0
        assert result['updated'] == 0
        assert result['skipped'] == 0
        
        mock_manager = create_mock_manager(issues=[], connect_success=False)
        result = process_issues_by_label(mock_manager, "rule-testing")
        assert result['success'] is False
        assert 'error' in result
        assert 'Failed to connect to Jira' in result['error']
        
        mock_manager = create_mock_manager(issues=[TEST_FIXTURE_ISSUES[2]])  # Already in target status
        
        result = process_issues_by_label(mock_manager, "rule-testing")
        assert result['success'] is True
        assert result['processed'] == 1
        assert result['updated'] == 0
        assert result['skipped'] == 1
        mock_manager.update_issue_status.assert_not_called()
    
    def test_user_can_use_workflow_commands(self):
        """Test that users can use the high-level workflow commands."""
        with patch('testfixture.workflow.JiraInstanceManager') as mock_manager_class, \
             patch('testfixture.workflow.process_issues_by_label') as mock_process:
            
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_process.return_value = create_reset_result(processed=1, updated=1)
            
            with patch('builtins.print'):
                run_TestFixture_Reset("https://jira.example.com", "user", "pass", "rule-testing")
            
            mock_manager_class.assert_called_once_with("https://jira.example.com", "user", "pass")
            mock_process.assert_called_once_with(mock_manager, "rule-testing")
        
        with patch('testfixture.workflow.JiraInstanceManager') as mock_manager_class, \
             patch('testfixture.workflow.assert_issues_expectations') as mock_assert:
            
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_assert.return_value = create_assert_result(processed=1, passed=1)
            
            with patch('builtins.print'):
                run_assert_expectations("https://jira.example.com", "user", "pass", "rule-testing")
            
            mock_manager_class.assert_called_once_with("https://jira.example.com", "user", "pass")
            mock_assert.assert_called_once_with(mock_manager, "rule-testing")


if __name__ == "__main__":
    pytest.main([__file__])
