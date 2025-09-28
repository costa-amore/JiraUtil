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
    issue_type = issue.get('issue_type', 'Unknown')
    rank = JiraInstanceManager.get_rank_value(issue)
    parent_key = issue.get('parent_key')
    
    # Parse expectation pattern
    expectation = extract_statuses_from_summary(summary)
    if not expectation:
        return {
            'key': key,
            'summary': summary,
            'status': current_status,
            'assert_result': None,  # Not evaluable
            'issue_type': issue_type,
            'parent_key': parent_key,
            'rank': rank,
            'evaluable': False
        }
    
    status1, expected_status = expectation
    
    context = extract_context_from_summary(summary)
    
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
        'issue_type': issue_type,
        'parent_key': parent_key,
        'rank': rank,
        'evaluable': True,
        'expected_status': expected_status,
        'context': context
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
    
    # Process non-failed results first
    for result in assertion_results:
        if not result['evaluable']:
            results['not_evaluated'] += 1
            results['not_evaluated_keys'].append(result['key'])
        elif result['assert_result'] == 'PASS':
            results['passed'] += 1
    
    # Group and sort failures hierarchically
    failed_results = [r for r in assertion_results if r['evaluable'] and r['assert_result'] == 'FAIL']
    results['failed'] = len(failed_results)
    
    # Group issues by epic relationships
    epics = {}
    stories = {}  # Track stories for sub-task relationships
    orphaned = []
    
    # First pass: collect all epics and stories (both evaluable and non-evaluable)
    for result in assertion_results:
        if result['issue_type'] == 'Epic':
            epics[result['key']] = result
        elif result['issue_type'] == 'Story':
            stories[result['key']] = result
    
    # Second pass: group failed results by epic relationships
    for result in failed_results:
        if result['issue_type'] == 'Epic':
            # Epic itself failed - already collected in first pass
            pass
        elif result.get('parent_key'):
            if result['parent_key'] not in epics:
                # Parent not found in our collection, create placeholder
                epics[result['parent_key']] = {'children': []}
            if 'children' not in epics[result['parent_key']]:
                epics[result['parent_key']]['children'] = []
            epics[result['parent_key']]['children'].append(result)
        elif result.get('parent_story'):
            # Sub-task with Story parent
            if result['parent_story'] not in stories:
                # Parent story not found in our collection, create placeholder
                stories[result['parent_story']] = {'children': []}
            if 'children' not in stories[result['parent_story']]:
                stories[result['parent_story']]['children'] = []
            stories[result['parent_story']]['children'].append(result)
        else:
            orphaned.append(result)
    
    # Third pass: add non-evaluable items that have children
    for result in assertion_results:
        if not result.get('evaluable', False):
            if result['issue_type'] == 'Story' and result['key'] in stories and 'children' in stories[result['key']]:
                # Non-evaluable story with children - add to epic's children
                if result.get('parent_key'):
                    if result['parent_key'] not in epics:
                        epics[result['parent_key']] = {'children': []}
                    if 'children' not in epics[result['parent_key']]:
                        epics[result['parent_key']]['children'] = []
                    epics[result['parent_key']]['children'].append(result)
            elif not result.get('parent_key') and not result.get('parent_story') and result['issue_type'] != 'Epic':
                # Non-evaluable orphaned item
                orphaned.append(result)
    
    # Sort epics by rank and add to failures
    sorted_epics = sorted(epics.values(), key=lambda x: (JiraInstanceManager.get_rank_value(x), x.get('key', '')))
    for epic in sorted_epics:
        if 'key' in epic:  # This is an actual epic
            if epic.get('evaluable', False):
                # Epic has assertion pattern - show assertion format
                context = f"{epic.get('context', '')} " if epic.get('context', '') else ""
                results['failures'].append(
                    f"[{epic['issue_type']}] {epic['key']}: {context}expected '{epic['expected_status']}' but is '{epic['status']}'"
                )
            else:
                # Epic has no assertion pattern - show full summary
                results['failures'].append(
                    f"[{epic['issue_type']}] {epic['key']}: {epic['summary']}"
                )
            
            # Add children sorted by rank
            if 'children' in epic:
                children = sorted(epic['children'], key=lambda x: (JiraInstanceManager.get_rank_value(x), x.get('key', '')))
                for child in children:
                    if child['issue_type'] == 'Story':
                        # Story child - check if it has sub-tasks
                        if child['key'] in stories and 'children' in stories[child['key']]:
                            # Story with sub-tasks - show story first
                            if child.get('evaluable', False):
                                context = f"{child.get('context', '')} " if child.get('context', '') else ""
                                results['failures'].append(
                                    f"  - [{child['issue_type']}] {child['key']}: {context}expected '{child['expected_status']}' but is '{child['status']}'"
                                )
                            else:
                                results['failures'].append(
                                    f"  - [{child['issue_type']}] {child['key']}: {child['summary']}"
                                )
                            
                            # Add sub-tasks indented under story
                            sub_tasks = sorted(stories[child['key']]['children'], key=lambda x: (JiraInstanceManager.get_rank_value(x), x.get('key', '')))
                            for sub_task in sub_tasks:
                                context = f"{sub_task.get('context', '')} " if sub_task.get('context', '') else ""
                                results['failures'].append(
                                    f"    - [{sub_task['issue_type']}] {sub_task['key']}: {context}expected '{sub_task['expected_status']}' but is '{sub_task['status']}'"
                                )
                        else:
                            # Story without sub-tasks - show normally
                            if child.get('evaluable', False):
                                context = f"{child.get('context', '')} " if child.get('context', '') else ""
                                results['failures'].append(
                                    f"  - [{child['issue_type']}] {child['key']}: {context}expected '{child['expected_status']}' but is '{child['status']}'"
                                )
                            else:
                                results['failures'].append(
                                    f"  - [{child['issue_type']}] {child['key']}: {child['summary']}"
                                )
                    else:
                        # Non-story child (shouldn't happen in current logic)
                        context = f"{child.get('context', '')} " if child.get('context', '') else ""
                        results['failures'].append(
                            f"  - [{child['issue_type']}] {child['key']}: {context}expected '{child['expected_status']}' but is '{child['status']}'"
                        )
    
    # Add orphaned issues sorted by rank
    orphaned.sort(key=lambda x: (JiraInstanceManager.get_rank_value(x), x.get('key', '')))
    for result in orphaned:
        if result.get('evaluable', False):
            # Orphaned item with assertion pattern - show assertion format
            context = f"{result.get('context', '')} " if result.get('context', '') else ""
            results['failures'].append(
                f"[{result['issue_type']}] {result['key']}: {context}expected '{result['expected_status']}' but is '{result['status']}'"
            )
        else:
            # Orphaned item without assertion pattern - show full summary
            results['failures'].append(
                f"[{result['issue_type']}] {result['key']}: {result['summary']}"
            )
    
    return results


