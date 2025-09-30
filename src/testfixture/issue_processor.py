"""
Issue processing functionality for test fixture management.

This module handles the core business logic for processing test fixture
issues, including status updates and expectation assertions.
"""

from typing import Dict, List
from jira_manager import JiraInstanceManager
from .patterns import extract_statuses_from_summary, extract_context_from_summary
from utils.colors import colored_print


# =============================================================================
# PUBLIC FUNCTIONS (sorted alphabetically)
# =============================================================================

def assert_testfixture_issues(jira_instance: JiraInstanceManager, testfixture_label: str) -> Dict:
    # Initialize results structure with report_data
    results = {
        'success': True,
        'processed': 0,
        'passed': 0,
        'failed': 0,
        'not_evaluated': 0,
        'assertion_results': [],
        'issues_to_report': [],
        'not_evaluated_keys': []
   }
    
    # Get issues with proper error handling
    issues_result = _get_issues_for_processing(jira_instance, testfixture_label)
    if not issues_result['success']:
        return issues_result
    
    issues = issues_result['issues']
    if not issues:
        return results
    
    # Sort issues by rank before processing to avoid duplication issues
    issues.sort(key=_order_by_rank_only)
    
    # Process each issue and collect results
    skipped_issues = []
    issues_to_list = []
    succeeded_issues = []
    
    for issue in issues:
        assertion_result = _process_single_issue_assertion(issue)
        _print_single_issue_progress(assertion_result)
        
        match assertion_result['assert_result']:
            case 'FAIL':
                issues_to_list.append(assertion_result)
            case 'PASS':
                succeeded_issues.append(assertion_result)
            case _:
                skipped_issues.append(assertion_result)

    # Sort issues by type category (sub-tasks first, then stories, then epics)
    issues_to_list.sort(key=_order_by_type_category)
    
    # Separate issues by type and identify orphans
    epics = []
    stories = []
    subtasks = []
    orphans = []
    
    for issue_to_list in issues_to_list:
        issue_type = issue_to_list.get('issue_type', 'Unknown')
        if issue_type == 'Epic':
            epics.append(issue_to_list)
        elif _i_am_an_orphan(issue_to_list, issues_to_list, skipped_issues, succeeded_issues):
            orphans.append(issue_to_list)
        elif issue_type == 'Sub-task':
            subtasks.append(issue_to_list)
        else:  # Story or other types
            stories.append(issue_to_list)
    
    # Build hierarchical report structure
    for epic_to_report in epics:
        results['issues_to_report'].append(epic_to_report)
        for story_to_report in _childrenOf(epic_to_report, stories):
            results['issues_to_report'].append(story_to_report)
            for subtask_to_report in _childrenOf(story_to_report, subtasks):
                results['issues_to_report'].append(subtask_to_report)
    
    for orphan_to_report in orphans:
        results['issues_to_report'].append(orphan_to_report)

    # Aggregate results from individual assertions
    assertion_results = skipped_issues + issues_to_list + succeeded_issues
    
    # Update results with aggregated data
    # Process non-failed results first
    for result in assertion_results:
        results['processed'] += 1
        if not result['evaluable']:
            results['not_evaluated'] += 1
            results['not_evaluated_keys'].append(result['key'])
        elif result['assert_result'] == 'PASS':
            results['passed'] += 1
    
    # Group and sort failures hierarchically
    failed_results = [r for r in assertion_results if r['evaluable'] and r['assert_result'] == 'FAIL']
    results['failed'] = len(failed_results)
    
    return results




def reset_testfixture_issues(jira_instance: JiraInstanceManager, testfixture_label: str, force_update_via=None) -> Dict:
    issues_result = _get_issues_for_processing(jira_instance, testfixture_label)
    if not issues_result['success']:
        return issues_result
    
    if not issues_result['issues']:
        return _create_empty_reset_results()
    
    return _process_issues_for_reset(issues_result['issues'], jira_instance, force_update_via)


# =============================================================================
# PRIVATE FUNCTIONS (sorted alphabetically)
# =============================================================================

def _build_assertion_result(issue: dict, evaluable: bool, assert_result: str = None, expected_status: str = None, context: str = None) -> dict:
    return {
        'key': issue['key'],
        'summary': issue['summary'],
        'status': issue['status'],
        'assert_result': assert_result,
        'issue_type': issue.get('issue_type', 'Unknown'),
        'parent_key': issue.get('parent_key'),
        'rank': JiraInstanceManager.get_rank_value(issue),
        'evaluable': evaluable,
        'expected_status': expected_status,
        'context': context
    }


def _could_skip_issue(current_status, starting_status):
    return current_status.upper() == starting_status.upper()


def _create_empty_reset_results():
    return _initialize_reset_results(0)


def _extract_issue_info(issue):
    return {
        'key': issue['key'],
        'summary': issue['summary'],
        'current_status': issue['status']
    }


def _force_update(issue_info, starting_status, intermediate_status, results, jira_instance):
    print(f"  Force updating via intermediate state '{intermediate_status}'")
    
    # First transition: current → intermediate
    if _perform_status_update(issue_info, intermediate_status, results, jira_instance):
        # Second transition: intermediate → starting
        if _perform_status_update(issue_info, starting_status, results, jira_instance):
            # correct for 2 updates for 1 issue
            results['updated'] -= 1 


def _get_issues_for_processing(jira_instance: JiraInstanceManager, testfixture_label: str) -> Dict:
    if not jira_instance.jira:
        if not jira_instance.connect():
            return {'success': False, 'error': 'Failed to connect to Jira'}
    
    issues = jira_instance.get_issues_by_label(testfixture_label)
    return {'success': True, 'issues': issues}


def _i_am_an_orphan(issue_to_list: dict, issues_to_list: list, skipped_issues: list, succeeded_issues: list) -> bool:
    parent_key = issue_to_list.get('parent_key')
    if not parent_key:  # i have no parent
        issue_to_list['parent_key'] = 'Orphan'
        return True

    if any(issue['key'] == parent_key for issue in issues_to_list):  
        return False

    for i, skipped_parent in enumerate(skipped_issues): # Look for parent in skipped_issues 
        if skipped_parent['key'] == parent_key:  # Move parent from skipped to issues_to_list
            issues_to_list.append(skipped_parent)
            skipped_issues.pop(i)
            return False

    for i, succeeded_parent in enumerate(succeeded_issues): # Look for parent in succeeded_issues 
        if succeeded_parent['key'] == parent_key:  # Move parent from succeeded to issues_to_list
            issues_to_list.append(succeeded_parent)
            succeeded_issues.pop(i)
            return False

    issue_to_list['parent_key'] = 'Orphan'
    return True


def _initialize_reset_results(issue_count):
    return {
        'success': True,
        'processed': issue_count,
        'updated': 0,
        'skipped': 0,
        'errors': []
    }


def _perform_status_update(issue_info, starting_status, results, jira_instance):
    print(f"  Starting status: {starting_status}")
    
    if _update_issue_status_safely(jira_instance, issue_info['key'], starting_status):
        results['updated'] += 1
        return True

    results['errors'].append(f"Failed to update {issue_info['key']}")
    return False


def _print_issue_processing_info(issue_info):
    print(f"Processing {issue_info['key']}: {issue_info['summary']}")
    print(f"  Current status: {issue_info['current_status']}")


def _print_single_issue_progress(result: dict) -> None:
    key = result['key']
    summary = result['summary']
    current_status = result['status']
    
    print(f"Asserting {key}: {summary}")
    print(f"  Current status: {current_status}")
    
    if not result['evaluable']:
        print(f"  Skipping - summary doesn't match expected pattern")
    else:
        expected_status = result['expected_status']
        print(f"  Expected status: {expected_status}")
        
        if result['assert_result'] == 'PASS':
            colored_print(f"  [OK] PASS - Current status matches expected status")
        else:
            colored_print(f"  [FAIL] FAIL - Current status '{current_status}' does not match expected status '{expected_status}'")


def _process_issues_for_reset(issues, jira_instance, force_update_via):
    results = _initialize_reset_results(len(issues))
    
    for issue in issues:
        _process_single_issue_reset(issue, results, jira_instance, force_update_via)
    
    return results


def _process_single_issue_assertion(issue: dict) -> dict:
    # Parse expectation pattern
    expectation = extract_statuses_from_summary(issue['summary'])
    if not expectation:
        return _build_assertion_result(issue, evaluable=False)
    
    start_status, expected_status = expectation
    context = extract_context_from_summary(issue['summary'])
    
    # Evaluate assertion
    if issue['status'].upper() == expected_status.upper():
        assert_result = 'PASS'
    else:
        assert_result = 'FAIL'
    
    return _build_assertion_result(
        issue, 
        evaluable=True, 
        assert_result=assert_result, 
        expected_status=expected_status, 
        context=context
    )


def _process_single_issue_reset(issue, results, jira_instance, force_update_via):
    issue_info = _extract_issue_info(issue)
    _print_issue_processing_info(issue_info)
    
    parse_result = extract_statuses_from_summary(issue_info['summary'])
    if not parse_result:
        _skip_issue_with_reason(issue_info, "summary doesn't match expected pattern", results)
        return
    
    starting_status, target_status = parse_result
    
    if _could_skip_issue(issue_info['current_status'], starting_status):
        if force_update_via:
            _force_update(issue_info, starting_status, force_update_via, results, jira_instance)
        else:
            _skip_issue_with_reason(issue_info, f"current status '{issue_info['current_status']}' already matches starting status '{starting_status}'", results)
        return
    
    _perform_status_update(issue_info, starting_status, results, jira_instance)


def _skip_issue_with_reason(issue_info, reason, results):
    print(f"  Skipping - {reason}")
    results['skipped'] += 1


def _update_issue_status_safely(jira_instance, key, status):
    try:
        return jira_instance.update_issue_status(key, status)
    except Exception as e:
        print(f"  Error updating {key} to {status}: {e}")
        return False


def _childrenOf(parent_issue: dict, children: list) -> list:
    return [child for child in children if child.get('parent_key') == parent_issue['key']]


def _order_by_rank_only(issue: dict):
    rank_value = issue.get('rank', '0|zzzzz:')
    return rank_value


def _order_by_type_category(issue: dict):
    # Primary sort: by issue type (Sub-task=0, Story=1, Epic=2)
    issue_type = issue.get('issue_type', 'Unknown')
    match issue_type:
        case 'Epic':
            type_priority = 2
        case 'Sub-task':
            type_priority = 0
        case _:
            type_priority = 1
    
    # Secondary sort: by LexoRank string (lexicographical comparison)
    # Jira uses LexoRank which should be sorted alphabetically
    rank_value = issue.get('rank', '0|zzzzz:')
    
    return (type_priority, rank_value)