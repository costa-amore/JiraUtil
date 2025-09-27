"""
Issue processing functionality for test fixture management.

This module handles the core business logic for processing test fixture
issues, including status updates and expectation assertions.
"""

from typing import Dict, List
from jira_manager import JiraInstanceManager
from .patterns import parse_summary_pattern, parse_expectation_pattern
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
        parse_result = parse_summary_pattern(summary)
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
    # Get issues with proper error handling
    issues_result = _get_issues_for_processing(jira_instance, testfixture_label)
    if not issues_result['success']:
        return issues_result
    
    issues = issues_result['issues']
    if not issues:
        return {
            'success': True, 
            'processed': 0, 
            'passed': 0, 
            'failed': 0, 
            'not_evaluated': 0,
            'assertion_results': []
        }
    
    # Process each issue and collect results
    assertion_results = []
    for issue in issues:
        assertion_result = _process_single_issue_assertion(issue)
        assertion_results.append(assertion_result)
    
    # Print assertion progress
    _print_assertion_progress(assertion_results)
    
    # Aggregate results from individual assertions
    results = _aggregate_assertion_results(assertion_results)
    
    return results


def _get_issues_for_processing(jira_instance: JiraInstanceManager, testfixture_label: str) -> Dict:
    if not jira_instance.jira:
        if not jira_instance.connect():
            return {'success': False, 'error': 'Failed to connect to Jira'}
    
    issues = jira_instance.get_issues_by_label(testfixture_label)
    return {'success': True, 'issues': issues}


def _print_assertion_progress(assertion_results: list) -> None:
    """
    Print assertion progress for each issue.
    
    Args:
        assertion_results: List of assertion result dictionaries
    """
    for result in assertion_results:
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


def _process_single_issue_assertion(issue: dict) -> dict:
    key = issue['key']
    summary = issue['summary']
    current_status = issue['status']
    
    # Parse expectation pattern
    expectation = parse_expectation_pattern(summary)
    if not expectation:
        return {
            'key': key,
            'summary': summary,
            'status': current_status,
            'assert_result': None,  # Not evaluable
            'issue_type': 'Unknown',  # Will be enhanced later
            'parent_epic': None,  # Will be enhanced later
            'rank': 0,  # Will be enhanced later
            'evaluable': False
        }
    
    status1, expected_status = expectation
    
    # Evaluate assertion
    if current_status.upper() == expected_status.upper():
        assert_result = 'PASS'
    else:
        assert_result = 'FAIL'
    
    return {
        'key': key,
        'summary': summary,
        'status': current_status,
        'assert_result': assert_result,
        'issue_type': 'Unknown',  # Will be enhanced later
        'parent_epic': None,  # Will be enhanced later
        'rank': 0,  # Will be enhanced later
        'evaluable': True,
        'expected_status': expected_status
    }


def _aggregate_assertion_results(assertion_results: list) -> dict:
    results = {
        'success': True,
        'processed': len(assertion_results),
        'passed': 0,
        'failed': 0,
        'not_evaluated': 0,
        'failures': [],
        'not_evaluated_keys': [],
        'assertion_results': assertion_results
    }
    
    for result in assertion_results:
        if not result['evaluable']:
            results['not_evaluated'] += 1
            results['not_evaluated_keys'].append(result['key'])
        elif result['assert_result'] == 'PASS':
            results['passed'] += 1
        elif result['assert_result'] == 'FAIL':
            results['failed'] += 1
            results['failures'].append(
                f"{result['key']}: Expected '{result['expected_status']}' but is '{result['status']}'"
            )
    
    return results


