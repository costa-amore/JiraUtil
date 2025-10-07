"""
Assert processing functionality for test fixture management.
"""

from typing import Dict
from jira_manager import JiraInstanceManager
from .issue_processor import (
    _get_issues_for_processing, _order_by_rank_only, _order_by_type_category,
    _i_am_an_orphan, _childrenOf, _process_single_issue_assertion, _print_single_issue_progress
)


def assert_testfixture_issues(jira_instance: JiraInstanceManager, test_set_label: str) -> Dict:
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
    issues_result = _get_issues_for_processing(jira_instance, test_set_label)
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
        for subtask_to_report in _childrenOf(orphan_to_report, subtasks):
            results['issues_to_report'].append(subtask_to_report)

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
