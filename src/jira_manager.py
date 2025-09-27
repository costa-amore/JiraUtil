"""
Generic Jira management functionality.

This module provides reusable Jira operations that can be used by various
Jira commands and integrations.
"""

from typing import List
from jira import JIRA
from jira.exceptions import JIRAError


class JiraInstanceManager:
    """Manages Jira instance operations and provides reusable functionality."""

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
                    'issue_type': issue.fields.issuetype.name
                })
            return result
        except JIRAError as e:
            print(f"Failed to search for issues with label '{label}': {e}")
            return []

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
            
            # Find transition that contains the status name enclosed in quotes
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
