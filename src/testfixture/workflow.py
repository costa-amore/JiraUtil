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
from .trigger_process import TriggerProcess


def run_TestFixture_Reset(jira_instance, testfixture_label: str) -> None:
    print(f"Starting process for issues with label '{testfixture_label}'...")
    
    results = reset_testfixture_issues(jira_instance, testfixture_label)
    report_reset_results(results)


def run_assert_expectations(jira_instance, testfixture_label: str) -> None:
    print(f"Starting assertion process for issues with label '{testfixture_label}'...")
    
    results = assert_testfixture_issues(jira_instance, testfixture_label)
    report_assertion_results(results)


def run_trigger_operation(jira_instance, issue_key: str, trigger_labels) -> None:
    """trigger by setting labels to the given issue"""
    if _is_multiple_labels(trigger_labels):
        labels = _parse_labels_string(trigger_labels)
    else:
        labels = [trigger_labels.strip() if isinstance(trigger_labels, str) else str(trigger_labels)]
        
    print(f"Starting trigger operation for issue '{issue_key}' with labels {labels}...")
    results = _set_labels_on_issue(jira_instance, issue_key, labels)    
    report_trigger_results(results)


def _is_multiple_labels(trigger_labels) -> bool:
    return isinstance(trigger_labels, str) and ',' in trigger_labels and trigger_labels.strip()


def _load_issue_and_labels(jira_instance, issue_key: str):
    issue = jira_instance.jira.issue(issue_key)
    current_labels = issue.fields.labels or []
    return issue, current_labels


def _parse_labels_string(labels_string: str) -> list:
    """Parse comma-separated labels string and return cleaned list."""
    if not labels_string or not labels_string.strip():
        return []
    
    # Split by comma and strip whitespace
    labels = [label.strip() for label in labels_string.split(',')]
    
    # Filter out empty strings
    return [label for label in labels if label]


def _add_label_to_issue(issue, label, current_labels):
    new_labels = list(current_labels) + [label]
    issue.update(fields={"labels": new_labels})
    print(f"INFO: Set labels {new_labels} on {issue.key}")


def _remove_label_from_issue(issue, label):
    current_labels = issue.fields.labels or []
    new_labels = [l for l in current_labels if l != label]
    issue.update(fields={"labels": new_labels})
    print(f"INFO: Removed label '{label}' from {issue.key}")


def _set_labels_on_issue(jira_instance, issue_key: str, labels: list) -> Dict:
    """Set labels on an issue. For single label, toggle behavior. For multiple labels, replace all."""
    if not labels or (len(labels) == 1 and not labels[0].strip()):
        print("FATAL ERROR: No valid labels provided")
        process = TriggerProcess(issue_key, "", [])
        return process.set_error("No valid labels provided").build_result()
    
    # Pass all labels to the builder
    process = TriggerProcess(issue_key, labels[0], labels)
    
    try:
        issue, current_labels = _load_issue_and_labels(jira_instance, issue_key)
        
        if len(labels) == 1:
            # Single label: toggle behavior (remove if present, then add)
            label = labels[0]
            if label in current_labels:
                _remove_label_from_issue(issue, label)
                process.mark_label_removed()
                issue, current_labels = _load_issue_and_labels(jira_instance, issue_key)
            
            _add_label_to_issue(issue, label, current_labels)
        else:
            # Multiple labels: toggle behavior (remove existing trigger labels, then add all trigger labels)
            # First, remove any existing trigger labels
            labels_to_remove = [label for label in labels if label in current_labels]
            if labels_to_remove:
                # Remove all trigger labels in one update
                new_labels = [label for label in current_labels if label not in labels_to_remove]
                issue.update(fields={"labels": new_labels})
                print(f"INFO: Removed labels {labels_to_remove} from {issue.key}")
                process.mark_label_removed()
                issue, current_labels = _load_issue_and_labels(jira_instance, issue_key)
            
            # Then, add all trigger labels in one update (with logging)
            new_labels = list(set(current_labels + labels))
            issue.update(fields={"labels": new_labels})
            print(f"INFO: Set labels {new_labels} on {issue.key}")
        
        return process.set_success(issue.fields.summary, current_labels).build_result()
    except Exception as e:
        print(f"FATAL ERROR: {str(e)}")
        return process.set_error(str(e)).build_result()



