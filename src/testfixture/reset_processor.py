"""
Reset processing functionality for test fixture management.
"""

from typing import Dict
from jira_manager import JiraInstanceManager
from .issue_processor import _get_issues_for_processing, _create_empty_reset_results, _process_issues_for_reset


def reset_testfixture_issues(jira_instance: JiraInstanceManager, testfixture_label: str, force_update_via=None) -> Dict:
    issues_result = _get_issues_for_processing(jira_instance, testfixture_label)
    if not issues_result['success']:
        return issues_result
    
    if not issues_result['issues']:
        return _create_empty_reset_results()
    
    return _process_issues_for_reset(issues_result['issues'], jira_instance, force_update_via)
