"""
Issue processing functionality for test fixture management.

This module handles the core business logic for processing test fixture
issues, including status updates and expectation assertions.
"""

from typing import Dict, List
from jira_manager import JiraInstanceManager
from .patterns import extract_statuses_from_summary, extract_context_from_summary
from utils.colors import colored_print


def reset_testfixture_issues(jira_instance: JiraInstanceManager, testfixture_label: str) -> Dict:
    # Get issues with proper error handling
    issues_result = _get_issues_for_processing(jira_instance, testfixture_label)
    if not issues_result['success']:
        return issues_result
    
    issues = issues_result['issues']
    if not issues:
        return {'success': True, 'processed': 0, 'updated': 0, 'skipped': 0}
    
    results = {
        'success': True,
        'processed': len(issues),
        'updated': 0,
        'skipped': 0,
        'errors': []
    }
    
    for issue in issues:
        key = issue['key']
        summary = issue['summary']
        current_status = issue['status']
        
        print(f"Processing {key}: {summary}")
        print(f"  Current status: {current_status}")
        
        # Parse summary pattern
        parse_result = extract_statuses_from_summary(summary)
        if not parse_result:
            print(f"  Skipping - summary doesn't match expected pattern")
            results['skipped'] += 1
            continue
        
        starting_status, target_status = parse_result
        
        # Check if current status already matches starting status
        if current_status.upper() == starting_status.upper():
            print(f"  Skipping - current status '{current_status}' already matches starting status '{starting_status}'")
            results['skipped'] += 1
            continue
        
        print(f"  Starting status: {starting_status}")
        
        # Update status using the jira_instance
        if jira_instance.update_issue_status(key, starting_status):
            results['updated'] += 1
        else:
            results['errors'].append(f"Failed to update {key}")
    
    return results


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

    epics = []
    stories = []
    subtasks = []
    orphans = []

    # add parents or identify orphans 
    issues_to_list.sort(key=order_by_type_category) # start at the bottom
    for issue_to_list in issues_to_list:
        issue_type = issue_to_list.get('issue_type', 'Unknown')
        if issue_type == 'Epic':
            epics.append(issue_to_list)
            continue

        if _i_am_an_orphan(issue_to_list, issues_to_list, skipped_issues, succeeded_issues):
            orphans.append(issue_to_list)
            continue
        
    for issue_to_list in issues_to_list:
        issue_type = issue_to_list.get('issue_type', 'Unknown')
        match issue_type:
            case 'Epic':
                if issue_to_list not in epics:  
                    epics.append(issue_to_list)
            case 'Sub-task':
                if issue_to_list not in subtasks:  
                    subtasks.append(issue_to_list)
            case _:
                if issue_to_list not in stories:  
                    stories.append(issue_to_list)

    issues_to_report = []
    for epic_to_report in epics:
        results['issues_to_report'].append(epic_to_report)
        for story_to_report in childrenOf(epic_to_report, stories):
            results['issues_to_report'].append(story_to_report)
            for subtask_to_report in childrenOf(story_to_report, subtasks):
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


def order_by_type_category(issue: dict):
    match issue.get('issue_type', 'Unknown'):
        case 'Epic':
            return 2
        case 'Sub-task':
            return 0
        case _:
            return 1


def _get_issues_for_processing(jira_instance: JiraInstanceManager, testfixture_label: str) -> Dict:
    if not jira_instance.jira:
        if not jira_instance.connect():
            return {'success': False, 'error': 'Failed to connect to Jira'}
    
    issues = jira_instance.get_issues_by_label(testfixture_label)
    return {'success': True, 'issues': issues}


def childrenOf(parent_issue: dict, children: list) -> list:
    return [child for child in children if child.get('parent_key') == parent_issue['key']]


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


def _print_assertion_progress(assertion_results: list) -> None:
    for result in assertion_results:
        _print_single_issue_progress(result)


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


def _aggregate_assertion_results(assertion_results: list) -> dict:
    return {}

