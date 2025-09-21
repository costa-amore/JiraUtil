"""
Jira Test module for rule-testing functionality.
Connects to Jira instance and manages rule-testing items based on summary patterns.
"""

import re
import os
from pathlib import Path
from typing import List, Optional, Tuple
from jira import JIRA
from jira.exceptions import JIRAError


class JiraInstanceManager:
    """Manages Jira instance operations and rule-testing functionality."""
    
    def __init__(self, jira_url: str, username: str, password: str):
        """
        Initialize Jira connection.
        
        Args:
            jira_url: Jira instance URL
            username: Jira username
            password: Jira password or API token
        """
        self.jira_url = jira_url
        self.username = username
        self.password = password
        self.jira = None
        
    def connect(self) -> bool:
        """
        Connect to Jira instance.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            print(f"DEBUG: Attempting to connect to {self.jira_url} with user {self.username}")
            self.jira = JIRA(
                server=self.jira_url,
                basic_auth=(self.username, self.password)
            )
            print("DEBUG: Successfully connected to Jira")
            return True
        except JIRAError as e:
            print(f"Failed to connect to Jira: {e}")
            return False
    
    def get_issues_by_label(self, label: str) -> List[dict]:
        """
        Get all issues with specified label.
        
        Args:
            label: Jira label to search for
            
        Returns:
            List of issue dictionaries with key, summary, and status
        """
        if not self.jira:
            print("Not connected to Jira. Call connect() first.")
            return []
        
        try:
            # Search for issues with specified label
            jql = f'labels = "{label}"'
            issues = self.jira.search_issues(jql, expand='changelog', fields='*all')
            
            result = []
            for issue in issues:
                result.append({
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'status': issue.fields.status.name,
                    'issue_obj': issue
                })
            
            return result
        except JIRAError as e:
            print(f"Failed to search for rule-testing issues: {e}")
            return []
    
    def parse_summary_pattern(self, summary: str) -> Optional[Tuple[str, str]]:
        """
        Parse summary to extract status1 and status2 from pattern:
        "I was in <status1> - expected to be in <status2>"
        
        Args:
            summary: Issue summary text
            
        Returns:
            Tuple of (status1, status2) if pattern matches, None otherwise
        """
        pattern = r"I was in (.+?) - expected to be in (.+)"
        match = re.search(pattern, summary, re.IGNORECASE)
        
        if match:
            status1 = match.group(1).strip()
            status2 = match.group(2).strip()
            return (status1, status2)
        
        return None
    
    def update_issue_status(self, issue_key: str, new_status: str) -> bool:
        """
        Update issue status.
        
        Args:
            issue_key: Jira issue key
            new_status: New status name
            
        Returns:
            True if update successful, False otherwise
        """
        if not self.jira:
            print("Not connected to Jira. Call connect() first.")
            return False
        
        try:
            # Get available transitions for the issue
            issue = self.jira.issue(issue_key)
            transitions = self.jira.transitions(issue)
            
            # Find transition that contains the target status name
            target_transition = None
            new_status_lower = new_status.lower()
            
            print(f"  Available transitions: {[t['name'] for t in transitions]}")
            
            # Search for transition that contains the status name enclosed in quotes
            quoted_status_pattern = f"\"{new_status_lower}\""
            for transition in transitions:
                if quoted_status_pattern in transition['name'].lower():
                    target_transition = transition
                    print(f"  Found transition: '{transition['name']}' contains '{quoted_status_pattern}'")
                    break
            
            if not target_transition:
                print(f"  No transition found containing status '{new_status}' for issue {issue_key}")
                return False
            
            # Perform the transition
            self.jira.transition_issue(issue, target_transition['id'])
            print(f"  Successfully updated {issue_key} to status '{new_status}' via transition '{target_transition['name']}'")
            return True
            
        except JIRAError as e:
            print(f"  Failed to update issue {issue_key}: {e}")
            return False
    
    def process_issues_by_label(self, label: str) -> dict:
        """
        Process all issues with specified label and update their status based on summary pattern.
        
        Args:
            label: Jira label to search for
            
        Returns:
            Dictionary with processing results
        """
        if not self.jira:
            if not self.connect():
                return {'success': False, 'error': 'Failed to connect to Jira'}
        
        issues = self.get_issues_by_label(label)
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
            parsed = self.parse_summary_pattern(summary)
            if not parsed:
                print(f"  Skipping - summary doesn't match expected pattern")
                results['skipped'] += 1
                continue
            
            status1, status2 = parsed
            print(f"  Parsed: was in '{status1}', expected to be in '{status2}'")
            
            # Check if current status already matches target status
            if current_status.upper() == status1.upper():
                print(f"  Skipping - current status '{current_status}' already matches target status '{status1}'")
                results['skipped'] += 1
                continue
            
            # Update status to status1
            if self.update_issue_status(key, status1):
                results['updated'] += 1
            else:
                results['errors'].append(f"Failed to update {key}")
        
        return results


def run_rule_testing(jira_url: str, username: str, password: str, label: str) -> None:
    """
    Run rule-testing process.
    
    Args:
        jira_url: Jira instance URL
        username: Jira username  
        password: Jira password or API token
        label: Jira label to search for
    """
    manager = JiraInstanceManager(jira_url, username, password)
    
    print(f"Starting process for issues with label '{label}'...")
    print(f"Connecting to Jira at: {jira_url}")
    
    results = manager.process_issues_by_label(label)
    
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
    
    if not jira_url:
        jira_url = input("Enter Jira URL: ").strip()
    
    if not username:
        username = input("Enter Jira username: ").strip()
    
    if not password:
        import getpass
        password = getpass.getpass("Enter Jira password/API token: ")
    
    return jira_url, username, password

