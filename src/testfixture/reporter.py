"""
Result reporting functionality for test fixture management.

This module handles formatting and displaying results from test fixture
operations including reset and assertion processes.
"""

from typing import Dict, List
from utils.colors import colored_print


# =============================================================================
# PUBLIC FUNCTIONS (sorted alphabetically)
# =============================================================================

def report_assertion_results(results: Dict) -> None:
    """
    Report results from the assertion test fixture operation.
    
    Args:
        results: Dictionary containing assertion operation results
    """
    if results['success']:
        print(f"\nAssertion process completed:")
        print(f"  Issues processed: {results['processed']}")
        print(f"  Assertions passed: {results['passed']}")
        print(f"  Assertions failed: {results['failed']}")
        print(f"  Not evaluated: {results['not_evaluated']}")
        
        if results.get('issues_to_report'):
            print(f"  Failures:")
            for issue in results['issues_to_report']:
                if issue['issue_type'] == 'Epic':
                    print(f"    - {_issue_to_list_in_failure_hierarchy(issue)}")
                elif issue['issue_type'] == 'Sub-task':
                    print(f"        - {_issue_to_list_in_failure_hierarchy(issue)}")
                else:
                  if issue['parent_key'] == 'Orphan':
                    print(f"    - {_issue_to_list_in_failure_hierarchy(issue)}")
                  else:
                    print(f"      - {_issue_to_list_in_failure_hierarchy(issue)}")
        
        if results.get('not_evaluated_keys'):
            keys_str = ", ".join(results['not_evaluated_keys'])
            print(f"  Not evaluated: {keys_str}")
        
        # Clear success/failure summary
        print(f"\n" + "="*60)
        if results['failed'] == 0:
            colored_print(f"[SUCCESS] ALL ASSERTIONS PASSED! [SUCCESS]")
            colored_print(f"[OK] All {results['passed']} evaluated issues are in their expected status")
        else:
            colored_print(f"[FAIL] ASSERTION FAILURES DETECTED! [FAIL]")
            colored_print(f"[WARN]  {results['failed']} out of {results['passed'] + results['failed']} evaluated issues are NOT in their expected status")
        print(f"="*60)
    else:
        print(f"Assertion process failed: {results.get('error', 'Unknown error')}")


def report_reset_results(results: Dict) -> None:
    """
    Report results from the reset test fixture operation.
    
    Args:
        results: Dictionary containing reset operation results
    """
    if results['success']:
        print(f"\nRule-testing process completed:")
        print(f"  Issues processed: {results['processed']}")
        print(f"  Issues updated: {results['updated']}")
        print(f"  Issues skipped: {results['skipped']}")
        
        if results.get('errors'):
            print(f"  Errors: {len(results['errors'])}")
            for error in results['errors']:
                print(f"    - {error}")
    else:
        print(f"Rule-testing process failed: {results.get('error', 'Unknown error')}")


def report_trigger_results(results: Dict) -> None:
    """
    Report results from the trigger test fixture operation.
    
    Args:
        results: Dictionary containing trigger operation results
    """
    if results['success']:
        print(f"\nTrigger operation completed:")
        print(f"  Issues processed: {results['processed']}")
        print(f"  Issues triggered: {results['triggered']}")
        
        if results.get('trigger_results'):
            for trigger_result in results['trigger_results']:
                print(f"  Issue: {trigger_result['key']}")
                print(f"  Labels set: {', '.join(trigger_result['trigger_labels'])}")
                if trigger_result.get('summary'):
                    print(f"  Summary: {trigger_result['summary']}")
    else:
        print(f"Trigger operation failed:")
        if results.get('errors'):
            for error in results['errors']:
                print(f"  - {error}")


# =============================================================================
# PRIVATE FUNCTIONS (sorted alphabetically)
# =============================================================================

def _issue_to_list_in_failure_hierarchy(issue: dict) -> str:
        return f"[{issue['issue_type']}] {issue['key']}: {issue['summary']}"