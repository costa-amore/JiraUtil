"""
Jira test fixture management functionality.

This module provides functionality to manage issues used as test fixtures,
primarily for verifying correct execution of automation rules. It uses the
generic Jira management capabilities from jira_manager.py.
"""

import os
import re
from pathlib import Path
from typing import Optional, Tuple
from jira_manager import JiraInstanceManager

# Shared pattern for both ResetTestFixture and AssertExpectations
SUMMARY_PATTERN = r"I was in (.+?) - expected to be in (.+)"

# Default label for test fixture issues (used to verify automation rules)
DEFAULT_TEST_FIXTURE_LABEL = "rule-testing"

def parse_summary_pattern(summary: str, current_status: str) -> Optional[Tuple[bool, str]]:
    """
    Parse issue summary to extract status names for rule-testing pattern.
    Expected pattern: "I was in <status1> - expected to be in <status2>"
    
    Args:
        summary: Issue summary text
        current_status: Current issue status
        
    Returns:
        Tuple of (should_update, target_status) if pattern matches, None otherwise
    """
    match = re.search(SUMMARY_PATTERN, summary, re.IGNORECASE)
    
    if match:
        status1 = match.group(1).strip()
        status2 = match.group(2).strip()
        
        # Check if current status already matches target status
        if current_status.upper() == status1.upper():
            print(f"  Skipping - current status '{current_status}' already matches target status '{status1}'")
            return (False, status1)
        
        return (True, status1)
    
    return None


def process_issues_by_label(manager: JiraInstanceManager, label: str) -> dict:
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
        parse_result = parse_summary_pattern(summary, current_status)
        if not parse_result:
            print(f"  Skipping - summary doesn't match expected pattern")
            results['skipped'] += 1
            continue
        
        should_update, target_status = parse_result
        if not should_update:
            print(f"  Skipping - no update needed")
            results['skipped'] += 1
            continue
        
        print(f"  Target status: {target_status}")
        
        # Update status using the manager
        if manager.update_issue_status(key, target_status):
            results['updated'] += 1
        else:
            results['errors'].append(f"Failed to update {key}")
    
    return results


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


def parse_expectation_pattern(summary: str) -> Optional[Tuple[str, str]]:
    """
    Parse issue summary to extract expected status for assertion pattern.
    Expected pattern: "I was in <status1> - expected to be in <status2>"
    
    Args:
        summary: Issue summary text
        
    Returns:
        Tuple of (status1, status2) if pattern matches, None otherwise
    """
    match = re.search(SUMMARY_PATTERN, summary, re.IGNORECASE)
    
    if match:
        status1 = match.group(1).strip()
        status2 = match.group(2).strip()
        return (status1, status2)
    
    return None


def assert_issues_expectations(manager: JiraInstanceManager, label: str) -> dict:
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
            print(f"  ✅ PASS - Current status matches expected status")
            results['passed'] += 1
        else:
            print(f"  ❌ FAIL - Current status '{current_status}' does not match expected status '{expected_status}'")
            results['failed'] += 1
            results['failures'].append(f"{key}: Expected '{expected_status}' but is '{current_status}'")
    
    return results


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
    
    if results['success']:
        print(f"\nAssertion process completed:")
        print(f"  Issues processed: {results['processed']}")
        print(f"  Assertions passed: {results['passed']}")
        print(f"  Assertions failed: {results['failed']}")
        print(f"  Not evaluated: {results['not_evaluated']}")
        
        if results.get('failures'):
            print(f"  Failures:")
            for failure in results['failures']:
                print(f"    - {failure}")
        
        if results.get('not_evaluated_keys'):
            keys_str = ", ".join(results['not_evaluated_keys'])
            print(f"  Not evaluated: {keys_str}")
        
        # Clear success/failure summary
        print(f"\n" + "="*60)
        if results['failed'] == 0:
            print(f"🎉 ALL ASSERTIONS PASSED! 🎉")
            print(f"✅ All {results['passed']} evaluated issues are in their expected status")
        else:
            print(f"❌ ASSERTION FAILURES DETECTED! ❌")
            print(f"⚠️  {results['failed']} out of {results['passed'] + results['failed']} evaluated issues are NOT in their expected status")
        print(f"="*60)
    else:
        print(f"Assertion process failed: {results.get('error', 'Unknown error')}")


def load_env_file(env_file_path: str) -> None:
    """
    Load environment variables from a .env file.
    
    Args:
        env_file_path: Path to the .env file
    """
    env_path = Path(env_file_path)
    if not env_path.exists():
        return
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ[key] = value


def get_jira_credentials() -> Tuple[str, str, str]:
    """
    Get Jira credentials from .env file, environment variables, or prompt user.
    
    Returns:
        Tuple of (jira_url, username, password)
    """
    # Try to load from .venv/jira_config.env first
    venv_config = Path('.venv') / 'jira_config.env'
    if venv_config.exists():
        load_env_file(str(venv_config))
    
    # Try to load from jira_config.env in current directory
    local_config = Path('jira_config.env')
    if local_config.exists():
        load_env_file(str(local_config))
    
    # Try to get from environment variables
    jira_url = os.getenv('JIRA_URL')
    username = os.getenv('JIRA_USERNAME')
    password = os.getenv('JIRA_PASSWORD')
    
    # Check if values are template/placeholder values
    def is_template_value(value, field_type):
        if not value or value.strip() == '':
            return True
        
        template_patterns = {
            'url': ['yourcompany', 'example', 'placeholder'],
            'username': ['your.email', 'example', 'placeholder', 'user@'],
            'password': ['your_api', 'example', 'placeholder', 'token_here']
        }
        
        value_lower = value.lower()
        for pattern in template_patterns.get(field_type, []):
            if pattern in value_lower:
                return True
        return False
    
    if is_template_value(jira_url, 'url'):
        jira_url = input("Enter Jira URL: ").strip()
    
    if is_template_value(username, 'username'):
        username = input("Enter Jira username: ").strip()
    
    if is_template_value(password, 'password'):
        import getpass
        password = getpass.getpass("Enter Jira password/API token: ")
    
    return jira_url, username, password