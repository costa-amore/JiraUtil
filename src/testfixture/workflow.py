"""
Workflow orchestration for test fixture management.

This module provides the main workflow functions that coordinate
test fixture operations including reset and assertion processes.
"""

from jira_manager import JiraInstanceManager
from auth import get_jira_credentials
from .issue_processor import process_issues_by_label, assert_issues_expectations
from .reporter import report_reset_results, report_assertion_results


def run_TestFixture_Reset(manager, label: str) -> None:
    """
    Run TestFixture reset process.
    
    Args:
        manager: Connected JiraInstanceManager
        label: Jira label to search for
    """
    print(f"Starting process for issues with label '{label}'...")
    
    # Use the ResetTestFixture specific process function
    results = process_issues_by_label(manager, label)
    report_reset_results(results)


def run_assert_expectations(manager, label: str) -> None:
    """
    Run assertion process for expectations.
    
    Args:
        manager: Connected JiraInstanceManager
        label: Jira label to search for
    """
    print(f"Starting assertion process for issues with label '{label}'...")
    
    # Use the AssertExpectations specific process function
    results = assert_issues_expectations(manager, label)
    report_assertion_results(results)


def run_trigger_operation(manager, label: str, issue_key: str) -> None:
    """
    Run trigger operation to toggle a label on a specific issue.

    Args:
        manager: Connected JiraInstanceManager
        label: Label to toggle
        issue_key: Key of the issue to modify
    """
    _toggle_label_on_issue(manager, issue_key, label)


def _toggle_label_on_issue(manager, issue_key: str, label: str) -> None:
    """Toggle a label on an issue by removing it if present, then adding it."""
    issue, current_labels = _load_issue_and_labels(manager, issue_key)
    
    if label in current_labels:
        _remove_label_from_issue(issue, label)
        issue, current_labels = _load_issue_and_labels(manager, issue_key)
    
    _add_label_to_issue(issue, label, current_labels)


def _load_issue_and_labels(manager, issue_key: str):
    """Load an issue and return it along with its current labels."""
    issue = manager.jira.issue(issue_key)
    current_labels = issue.fields.labels or []
    return issue, current_labels


def _remove_label_from_issue(issue, label):
    """Remove the specified label from the issue."""
    current_labels = issue.fields.labels or []
    new_labels = [l for l in current_labels if l != label]
    issue.update(fields={"labels": new_labels})


def _add_label_to_issue(issue, label, current_labels):
    """Add the specified label to the issue."""
    new_labels = list(current_labels) + [label]
    issue.update(fields={"labels": new_labels})