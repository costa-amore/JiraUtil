"""
Test fixture scenarios for verifying Jira automation rules.

This module contains complete test scenarios that group test data
with expected results for test fixture operations.
"""

from .base_fixtures import create_mock_manager_with_expected_results

# Test fixture issue data
TEST_FIXTURE_ISSUES = [
    {
        'key': 'PROJ-1',
        'summary': 'I was in To Do - expected to be in In Progress',
        'status': 'In Progress'  # Needs update to To Do
    },
    {
        'key': 'PROJ-2',
        'summary': 'Bug fix - starting in In Progress - expected to be in Done',
        'status': 'Done'  # Needs update to In Progress
    },
    {
        'key': 'PROJ-3',
        'summary': 'starting in To Do - expected to be in In Progress',
        'status': 'To Do'  # Already in target status
    }
]

# Test fixture issues for assert tests (different statuses for pass/fail scenarios)
TEST_FIXTURE_ASSERT_ISSUES = [
    {
        'key': 'PROJ-1',
        'summary': 'I was in To Do - expected to be in In Progress',
        'status': 'In Progress',  # Matches expected status
        'issue_type': 'Story'
    },
    {
        'key': 'PROJ-2',
        'summary': 'starting in In Progress - expected to be in Done',
        'status': 'To Do',  # Does not match expected status
        'issue_type': 'Bug'
    }
]

# Test fixture command test data
TEST_FIXTURE_SINGLE_COMMANDS = [
    (['test-fixture', 'reset', '-l', 'custom-label'], 'test-fixture', 'reset', 'custom-label'),
    (['tf', 'r', '-l', 'rule-testing'], 'tf', 'r', 'rule-testing'),
    (['test-fixture', 'assert', '-l', 'custom-label'], 'test-fixture', 'assert', 'custom-label'),
    (['tf', 'a', '-l', 'rule-testing'], 'tf', 'a', 'rule-testing'),
]

TEST_FIXTURE_CHAINED_COMMANDS = [
    (['test-fixture', 'r', 't', '-l', 'custom-label'], 'test-fixture', ['r', 't'], 'custom-label'),
    (['tf', 'r', 'a', 't', '-l', 'rule-testing'], 'tf', ['r', 'a', 't'], 'rule-testing'),
    (['test-fixture', 'r', 'r', 'r', 't', '-l', 'custom-label'], 'test-fixture', ['r', 'r', 'r', 't'], 'custom-label'),
    (['tf', 'a', 'r', 'a', 't', 'a', 'a', 'a', 'a', '-l', 'rule-testing'], 'tf', ['a', 'r', 'a', 't', 'a', 'a', 'a', 'a'], 'rule-testing'),
]


# =============================================================================
# PUBLIC FUNCTIONS (sorted alphabetically)
# =============================================================================

def create_assert_result(processed=0, passed=0, failed=0, not_evaluated=0, failures=None, not_evaluated_keys=None, success=True):
    """Create a standard assert result dictionary."""
    return {
        'success': success,
        'processed': processed,
        'passed': passed,
        'failed': failed,
        'not_evaluated': not_evaluated,
        'failures': failures or [],
        'not_evaluated_keys': not_evaluated_keys or []
    }


def create_assert_scenario(issue_type="Story", issue_key="PROJ-1", summary="I have a dream", rank=None):
    """Create a custom assert scenario with specific issue parameters."""
    from unittest.mock import Mock
    mock_manager = Mock()
    issue = {
        'key': issue_key,
        'summary': summary,
        'status': 'To Do',
        'issue_type': issue_type,
        'epic_link': None,
        'rank': 0
    }
    if rank is not None:
        issue['rank'] = rank
    mock_manager.get_issues_by_label.return_value = [issue]
    return mock_manager


def create_assert_scenario_with_expectations():
    """Create a complete assert scenario with both test data and expected results."""
    # Test data: 2 issues after automation rules have run (1 pass, 1 fail)
    issues_for_assertion = TEST_FIXTURE_ASSERT_ISSUES
    
    # Expected results: Both issues processed, 1 passed, 1 failed
    return create_mock_manager_with_expected_results(
        issues=issues_for_assertion,
        expected_success=True,
        expected_processed=2,      # Both issues processed
        expected_updated=0,        # Assert doesn't update, just checks
        expected_skipped=0,        # No issues skipped
        expected_errors=[]         # No errors
    )


def create_connection_failure_scenario_with_expectations():
    """Create a connection failure scenario with expected results."""
    # Test data: No issues (connection fails before we can get them)
    empty_issues = []
    
    # Expected results: Connection failure, no processing
    return create_mock_manager_with_expected_results(
        issues=empty_issues,
        expected_success=False,    # Connection failed
        expected_processed=0,      # No processing
        expected_updated=0,        # No updates
        expected_skipped=0,        # No skips
        expected_errors=['Failed to connect to Jira']  # Connection error
    )


def create_empty_scenario_with_expectations():
    """Create an empty scenario with expected results."""
    # Test data: No issues found
    empty_issues = []
    
    # Expected results: No processing, all counts zero
    return create_mock_manager_with_expected_results(
        issues=empty_issues,
        expected_success=True,
        expected_processed=0,      # No issues to process
        expected_updated=0,        # No updates
        expected_skipped=0,        # No skips
        expected_errors=[]         # No errors
    )


def create_reset_result(processed=0, updated=0, skipped=0, errors=None, success=True):
    """Create a standard reset result dictionary."""
    return {
        'success': success,
        'processed': processed,
        'updated': updated,
        'skipped': skipped,
        'errors': errors or []
    }


def create_reset_scenario_with_expectations():
    """Create a complete reset scenario with both test data and expected results."""
    # Test data: 2 issues that need status reset
    issues_that_need_reset = TEST_FIXTURE_ISSUES[:2]
    
    # Expected results: Both issues should be processed and updated
    return create_mock_manager_with_expected_results(
        issues=issues_that_need_reset,
        expected_success=True,
        expected_processed=2,      # Both issues processed
        expected_updated=2,        # Both issues updated
        expected_skipped=0,        # No issues skipped
        expected_errors=[]         # No errors
    )


def create_skip_scenario_with_expectations():
    """Create a scenario where issues are already in starting status."""
    # Test data: Issue already in starting status (no update needed)
    issues_already_in_starting_status = [TEST_FIXTURE_ISSUES[2]]  # Already in "To Do"
    
    # Expected results: Issue processed but skipped (no update)
    return create_mock_manager_with_expected_results(
        issues=issues_already_in_starting_status,
        expected_success=True,
        expected_processed=1,      # One issue processed
        expected_updated=0,        # No updates (already in correct status)
        expected_skipped=1,        # One issue skipped
        expected_errors=[]         # No errors
    )


def reset_scenario_with(issue_key):
    """Create a reset scenario builder for the given issue key."""
    return ResetScenarioBuilder(issue_key)


# =============================================================================
# CLASSES (sorted alphabetically)
# =============================================================================

class ResetScenarioBuilder:
    """Builder for creating reset test scenarios with explicit data."""
    
    def __init__(self, issue_key):
        self.issue_key = issue_key
        self.starting_state = None
        self.current_state = None
        self.summary = None
    
    def and_current_state(self, state):
        self.current_state = state
        return self
    
    def and_starting_state(self, state):
        self.starting_state = state
        return self
    
    def create_scenario(self):
        """Create a mock manager with the configured scenario."""
        from unittest.mock import Mock
        
        # Generate summary if not provided
        if not self.summary:
            self.summary = f"I was in {self.starting_state} - expected to be in In Progress"
        
        issue = {
            'key': self.issue_key,
            'summary': self.summary,
            'status': self.current_state
        }
        
        # Create mock manager with the issue
        mock_manager = Mock()
        mock_manager.get_issues_by_label.return_value = [issue]
        mock_manager.update_issue_status.return_value = True
        
        return mock_manager
    
    def with_summary(self, summary):
        self.summary = summary
        return self