from typing import Dict, List
from utils.colors import colored_print


def report_assertion_results(results: Dict) -> None:
    """Report results from the assertion test fixture operation."""
    output_lines = _generate_assertion_report_lines(results)
    for line in output_lines:
        colored_print(line)


def _generate_assertion_report_lines(results: Dict) -> List[str]:
    """Generate the lines that would be printed for assertion results."""
    lines = []
    if results['success']:
        lines.append(f"\nAssertion process completed:")
        lines.append(f"  Issues processed: {results['processed']}")
        lines.append(f"  Assertions passed: {results['passed']}")
        lines.append(f"  Assertions failed: {results['failed']}")
        lines.append(f"  Not evaluated: {results['not_evaluated']}")
        
        if results.get('issues_to_report'):
            lines.append(f"  Failures:")
            for issue in results['issues_to_report']:
                if issue['issue_type'] == 'Epic':
                    lines.append(f"    - {_issue_to_list_in_failure_hierarchy(issue)}")
                elif issue['issue_type'] == 'Sub-task':
                    lines.append(f"        - {_issue_to_list_in_failure_hierarchy(issue)}")
                else:
                  if issue['parent_key'] == 'Orphan':
                    lines.append(f"    - {_issue_to_list_in_failure_hierarchy(issue)}")
                  else:
                    lines.append(f"      - {_issue_to_list_in_failure_hierarchy(issue)}")
        
        if results.get('not_evaluated_keys'):
            keys_str = ", ".join(results['not_evaluated_keys'])
            lines.append(f"  Not evaluated: {keys_str}")
        
        lines.append(f"\n" + "="*60)
        if results['failed'] == 0:
            lines.append(f"[SUCCESS] ALL ASSERTIONS PASSED! [SUCCESS]")
            lines.append(f"[OK] All {results['passed']} evaluated issues are in their expected status")
        else:
            lines.append(f"[FAIL] ASSERTION FAILURES DETECTED! [FAIL]")
            lines.append(f"[WARN]  {results['failed']} out of {results['passed'] + results['failed']} evaluated issues are NOT in their expected status")
        lines.append(f"="*60)
    else:
        lines.append(f"Assertion process failed: {results.get('error', 'Unknown error')}")
    
    return lines


def report_reset_results(results: Dict) -> None:
    """Report results from the reset test fixture operation."""
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
    """Report results from the trigger test fixture operation."""
    if results['success']:
        print(f"\nTrigger operation completed:")
        print(f"  Issues processed: {results['processed']}")
        print(f"  Issues triggered: {results['triggered']}")
        
        if results.get('trigger_results'):
            for trigger_result in results['trigger_results']:
                print(f"  Issue: {trigger_result['key']}")
                if trigger_result.get('was_removed'):
                    print(f"  Labels Removed: {', '.join(trigger_result['trigger_labels'])}")
                print(f"  Labels Set: {', '.join(trigger_result['trigger_labels'])}")
                if trigger_result.get('summary'):
                    print(f"  Summary: {trigger_result['summary']}")
    else:
        print(f"Trigger operation failed:")
        if results.get('errors'):
            for error in results['errors']:
                print(f"  - {error}")


def _issue_to_list_in_failure_hierarchy(issue: dict) -> str:
    """Format issue for display in failure hierarchy."""
    # Determine color tag based on evaluation status
    if issue.get('evaluable', True):  # Default to evaluable if not specified
        color_tag = "[FAIL]"
    else:
        color_tag = "[INFO]"
    
    return f"{color_tag} [{issue['issue_type']}] {issue['key']}: {issue['summary']}"