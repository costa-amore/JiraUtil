"""
Test fixture scenarios for verifying Jira automation rules.

This module contains complete test scenarios that group test data
with expected results for test fixture operations.
"""

from .base_fixtures import create_mock_manager_with_expected_results, TEST_FIXTURE_ISSUES, TEST_FIXTURE_ASSERT_ISSUES


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
