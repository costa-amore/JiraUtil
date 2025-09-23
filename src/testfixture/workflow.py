"""
Workflow orchestration for test fixture management.

This module provides the main workflow functions that coordinate
test fixture operations including reset and assertion processes.
"""

from jira_manager import JiraInstanceManager
from auth import get_jira_credentials
from .issue_processor import process_issues_by_label, assert_issues_expectations
from .reporter import report_reset_results, report_assertion_results


def run_TestFixture_Reset(jira_url: str, username: str, password: str, label: str) -> None:
    """
    Run TestFixture reset process.
    
    Args:
        jira_url: Jira instance URL
        username: Jira username  
        password: Jira password or API token
        label: Jira label to search for
    """
    manager = JiraInstanceManager(jira_url, username, password)
    
    print(f"Starting process for issues with label '{label}'...")
    print(f"Connecting to Jira at: {jira_url}")
    
    # Use the ResetTestFixture specific process function
    results = process_issues_by_label(manager, label)
    report_reset_results(results)


def run_assert_expectations(jira_url: str, username: str, password: str, label: str) -> None:
    """
    Run assertion process for expectations.
    
    Args:
        jira_url: Jira instance URL
        username: Jira username  
        password: Jira password or API token
        label: Jira label to search for
    """
    manager = JiraInstanceManager(jira_url, username, password)
    
    print(f"Starting assertion process for issues with label '{label}'...")
    print(f"Connecting to Jira at: {jira_url}")
    
    # Use the AssertExpectations specific process function
    results = assert_issues_expectations(manager, label)
    report_assertion_results(results)
