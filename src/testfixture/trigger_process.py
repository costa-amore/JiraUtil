"""
Trigger process builder for collecting information during trigger operations.

This module provides the TriggerProcess builder class that collects information
during the trigger process and builds a standardized result at the end.
"""

from typing import Dict, List


class TriggerProcess:
    """Builder class for collecting trigger process information."""
    
    def __init__(self, issue_key: str, label: str, all_labels: List[str] = None):
        self.issue_key = issue_key
        self.label = label  # Primary label for reporting
        self.all_labels = all_labels or [label]  # All labels being set
        self.success = False
        self.error = None
        self.was_removed = False
        self.issue_summary = None
        self.previous_labels = []
    
    def set_success(self, issue_summary: str, previous_labels: List[str]) -> 'TriggerProcess':
        """Mark the process as successful with details."""
        self.success = True
        self.issue_summary = issue_summary
        self.previous_labels = previous_labels
        return self
    
    def mark_label_removed(self) -> 'TriggerProcess':
        """Mark that a label was removed during the process."""
        self.was_removed = True
        return self
    
    def set_error(self, error: str) -> 'TriggerProcess':
        """Mark the process as failed with error details."""
        self.success = False
        self.error = error
        return self
    
    def build_result(self) -> Dict:
        """Build the final result dictionary."""
        return {
            'success': self.success,
            'processed': 1,
            'triggered': 1 if self.success else 0,
            'errors': [f"{self.issue_key}: {self.error}"] if self.error else [],
            'trigger_results': [{
                'key': self.issue_key,
                'summary': self.issue_summary or 'Unknown',
                'trigger_labels': self.all_labels,
                'previous_labels': self.previous_labels,
                'success': self.success,
                'error': self.error,
                'was_removed': self.was_removed
            }]
        }
