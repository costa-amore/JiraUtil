"""
Workflow orchestration for test fixture management.

This module provides the main workflow functions that coordinate
test fixture operations including reset and assertion processes.
"""

from typing import Dict
from jira_manager import JiraInstanceManager
from auth import get_jira_credentials
from .issue_processor import reset_testfixture_issues, assert_testfixture_issues
from .reporter import report_reset_results, report_assertion_results, report_trigger_results


def run_TestFixture_Reset(jira_instance, testfixture_label: str, force_update_via=None) -> None:
    print(f"Starting process for issues with label '{testfixture_label}'...")
    
    results = reset_testfixture_issues(jira_instance, testfixture_label)
    report_reset_results(results)


def run_assert_expectations(jira_instance, testfixture_label: str) -> None:
    print(f"Starting assertion process for issues with label '{testfixture_label}'...")
    
    results = assert_testfixture_issues(jira_instance, testfixture_label)
    report_assertion_results(results)


def run_trigger_operation(jira_instance, issue_key: str, trigger_labels) -> None:
    labels = _parse_labels_string(trigger_labels)        
    print(f"Starting trigger operation for issue '{issue_key}' with labels {labels}...")

    results = _set_labels_on_issue(jira_instance, issue_key, labels)    
    report_trigger_results(results)


def _load_issue_and_labels(jira_instance, issue_key: str):
    issue = jira_instance.jira.issue(issue_key)
    current_labels = issue.fields.labels or []
    return issue, current_labels


def _parse_labels_string(labels_input) -> list:
    if not labels_input:
        return []
    
    # Convert to string if not already
    labels_string = str(labels_input).strip()
    if not labels_string:
        return []
    
    # Split by comma and strip whitespace
    labels = [label.strip() for label in labels_string.split(',')]
    
    # Filter out empty strings
    return [label for label in labels if label]


def _set_labels_on_issue(jira_instance, issue_key: str, labels: list) -> Dict:
    if not labels or (len(labels) == 1 and not labels[0].strip()):
        print("FATAL ERROR: No valid labels provided")
        return _build_trigger_result(issue_key, labels, success=False, error="No valid labels provided")
    
    try:
        issue, current_labels = _load_issue_and_labels(jira_instance, issue_key)
        
        # Check if any trigger labels were already present (for reporting)
        needs_toggle = any(label in current_labels for label in labels)
        
        if needs_toggle:
            # toggle OFF: Remove existing trigger labels first
            labels_after_removal = [label for label in current_labels if label not in labels]
            issue.update(fields={"labels": labels_after_removal})
            
            # Wait for JIRA to digest the toggle
            print("Waiting for JIRA to digest the toggle...")
            import time
            FIVE_SECONDS = 5
            time.sleep(FIVE_SECONDS)

            # proceed with toggle ON
        
        # Add all labels
        new_labels = list(set(current_labels + labels))
        issue.update(fields={"labels": new_labels})
        
        return _build_trigger_result(issue_key, labels, success=True, issue_summary=issue.fields.summary, was_removed=needs_toggle)
    except Exception as e:
        print(f"FATAL ERROR: {str(e)}")
        return _build_trigger_result(issue_key, labels, success=False, error=str(e))


def _build_trigger_result(issue_key: str, labels: list, success: bool, issue_summary: str = None, was_removed: bool = False, error: str = None) -> Dict:
    """Build a simple trigger result dictionary."""
    return {
        'success': success,
        'processed': 1,
        'triggered': 1 if success else 0,
        'errors': [f"{issue_key}: {error}"] if error else [],
        'trigger_results': [{
            'key': issue_key,
            'summary': issue_summary or 'Unknown',
            'trigger_labels': labels,
            'success': success,
            'error': error,
            'was_removed': was_removed
        }]
    }



