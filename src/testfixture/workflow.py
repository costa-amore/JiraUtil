"""
Workflow orchestration for test fixture management.

This module provides the main workflow functions that coordinate
test fixture operations including reset and assertion processes.
"""

from typing import Dict
from jira_manager import JiraInstanceManager
from auth import get_jira_credentials
from .reset_processor import reset_testfixture_issues
from .assert_processor import assert_testfixture_issues
from .trigger_processor import run_trigger_operation
from .reporter import report_reset_results, report_assertion_results


def run_TestFixture_Reset(jira_instance, test_set_label: str, force_update_via=None) -> None:
    print(f"Starting process for issues with test-set-label '{test_set_label}'...")
    
    results = reset_testfixture_issues(jira_instance, test_set_label, force_update_via)
    report_reset_results(results)


def run_assert_expectations(jira_instance, test_set_label: str) -> None:
    print(f"Starting assertion process for issues with test-set-label '{test_set_label}'...")
    
    results = assert_testfixture_issues(jira_instance, test_set_label)
    report_assertion_results(results)

