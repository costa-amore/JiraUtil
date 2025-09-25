"""
Issue processing functionality for test fixture management.

This module handles the core business logic for processing test fixture
issues, including status updates and expectation assertions.
"""

from typing import Dict, List
from jira_manager import JiraInstanceManager
from .patterns import parse_summary_pattern, parse_expectation_pattern
from utils.colors import colored_print


def process_issues_by_label(manager: JiraInstanceManager, label: str) -> Dict:
    """
    Process all issues with specified label and update their status based on summary pattern.
    This is specific to the ResetTestFixture operation.
    
    Args:
        manager: JiraInstanceManager instance
        label: Jira label to search for
        
    Returns:
        Dictionary with processing results
    """
    if not manager.jira:
        if not manager.connect():
            return {'success': False, 'error': 'Failed to connect to Jira'}
    
    issues = manager.get_issues_by_label(label)
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
        
        # Update status using the manager
        if manager.update_issue_status(key, starting_status):
            results['updated'] += 1
        else:
            results['errors'].append(f"Failed to update {key}")
    
    return results


def assert_issues_expectations(manager: JiraInstanceManager, label: str) -> Dict:
    """
    Assert that all issues with specified label are in their expected status.
    This is specific to the AssertExpectations operation.
    
    Args:
        manager: JiraInstanceManager instance
        label: Jira label to search for
        
    Returns:
        Dictionary with assertion results
    """
    if not manager.jira:
        if not manager.connect():
            return {'success': False, 'error': 'Failed to connect to Jira'}
    
    issues = manager.get_issues_by_label(label)
    if not issues:
        return {'success': True, 'processed': 0, 'passed': 0, 'failed': 0, 'not_evaluated': 0}
    
    results = {
        'success': True,
        'processed': len(issues),
        'passed': 0,
        'failed': 0,
        'not_evaluated': 0,
        'failures': [],
        'not_evaluated_keys': []
    }
    
    for issue in issues:
        key = issue['key']
        summary = issue['summary']
        current_status = issue['status']
        
        print(f"Asserting {key}: {summary}")
        print(f"  Current status: {current_status}")
        
        # Parse expectation pattern
        expectation = parse_expectation_pattern(summary)
        if not expectation:
            print(f"  Skipping - summary doesn't match expected pattern")
            results['not_evaluated'] += 1
            results['not_evaluated_keys'].append(key)
            continue
        
        status1, expected_status = expectation
        print(f"  Expected status: {expected_status}")
        
        # Assert that current status matches expected status
        if current_status.upper() == expected_status.upper():
            colored_print(f"  [OK] PASS - Current status matches expected status")
            results['passed'] += 1
        else:
            colored_print(f"  [FAIL] FAIL - Current status '{current_status}' does not match expected status '{expected_status}'")
            results['failed'] += 1
            results['failures'].append(f"{key}: Expected '{expected_status}' but is '{current_status}'")
    
    return results
