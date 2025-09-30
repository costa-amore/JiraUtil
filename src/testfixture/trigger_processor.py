"""
Trigger processing functionality for test fixture management.
"""

from typing import Dict
from jira_manager import JiraInstanceManager
from .reporter import report_trigger_results


def run_trigger_operation(jira_instance, issue_key: str, trigger_labels) -> None:
    trigger_labels_list = _parse_labels_string(trigger_labels)        
    print(f"Starting trigger operation for issue '{issue_key}' with trigger-labels {trigger_labels_list}...")
    
    results = _set_labels_on_issue(jira_instance, issue_key, trigger_labels_list)
    report_trigger_results(results)


# =============================================================================
# PRIVATE FUNCTIONS (sorted alphabetically)
# =============================================================================

def _build_trigger_result(issue_key: str, trigger_labels: list, success: bool, issue_summary: str = None, was_removed: bool = False, error: str = None) -> Dict:
    """Build a simple trigger result dictionary."""
    return {
        'success': success,
        'processed': 1,
        'triggered': 1 if success else 0,
        'errors': [f"{issue_key}: {error}"] if error else [],
        'trigger_results': [{
            'key': issue_key,
            'summary': issue_summary or 'Unknown',
            'trigger_labels': trigger_labels,
            'success': success,
            'error': error,
            'was_removed': was_removed
        }]
    }


def _load_issue_and_labels(jira_instance, issue_key: str):
    issue = jira_instance.jira.issue(issue_key)
    current_trigger_labels = issue.fields.labels or []
    return issue, current_trigger_labels


def _parse_labels_string(trigger_labels_input) -> list:
    if not trigger_labels_input:
        return []
    
    # Convert to string if not already
    trigger_labels_string = str(trigger_labels_input).strip()
    if not trigger_labels_string:
        return []
    
    # Split by comma and strip whitespace
    trigger_labels = [trigger_label.strip() for trigger_label in trigger_labels_string.split(',')]
    
    # Filter out empty strings
    return [trigger_label for trigger_label in trigger_labels if trigger_label]


def _set_labels_on_issue(jira_instance, issue_key: str, trigger_labels: list) -> Dict:
    if not trigger_labels or (len(trigger_labels) == 1 and not trigger_labels[0].strip()):
        print("FATAL ERROR: No valid trigger-labels provided")
        return _build_trigger_result(issue_key, trigger_labels, success=False, error="No valid trigger-labels provided")
    
    try:
        issue, current_trigger_labels = _load_issue_and_labels(jira_instance, issue_key)
        
        # Check if any trigger-labels were already present (for reporting)
        needs_toggle = any(trigger_label in current_trigger_labels for trigger_label in trigger_labels)
        
        if needs_toggle:
            # toggle OFF: Remove existing trigger-labels first
            trigger_labels_after_removal = [trigger_label for trigger_label in current_trigger_labels if trigger_label not in trigger_labels]
            issue.update(fields={"labels": trigger_labels_after_removal})
            
            # Wait for JIRA to digest the toggle
            print("Waiting for JIRA to digest the toggle...")
            import time
            FIVE_SECONDS = 5
            time.sleep(FIVE_SECONDS)

            # proceed with toggle ON
        
        # Add all trigger-labels
        new_trigger_labels = list(set(current_trigger_labels + trigger_labels))
        issue.update(fields={"labels": new_trigger_labels})
        
        return _build_trigger_result(issue_key, trigger_labels, success=True, issue_summary=issue.fields.summary, was_removed=needs_toggle)
    except Exception as e:
        print(f"FATAL ERROR: {str(e)}")
        return _build_trigger_result(issue_key, trigger_labels, success=False, error=str(e))
