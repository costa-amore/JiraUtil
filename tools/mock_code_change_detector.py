#!/usr/bin/env python3
"""
Mock code change detector for testing purposes.
Allows tests to control whether code changes are detected.
"""

from typing import List


class MockCodeChangeDetector:
    """Mock implementation of CodeChangeDetector for testing."""
    
    def __init__(self, has_changes: bool = True):
        """
        Initialize mock detector.
        
        Args:
            has_changes: Whether to report that code has changed
        """
        self.has_changes = has_changes
        self._changed_files = []
    
    def has_code_changed(self) -> bool:
        """Return whether code has changed (controlled by test)."""
        return self.has_changes
    
    def get_changed_files(self) -> List[str]:
        """Return list of changed files (controlled by test)."""
        return self._changed_files
    
    def update_hashes(self) -> None:
        """Mock implementation - does nothing."""
        pass
    
    def mark_build_complete(self) -> None:
        """Mock implementation - does nothing."""
        pass
    
    def set_has_changes(self, has_changes: bool) -> None:
        """Set whether code has changed (for test control)."""
        self.has_changes = has_changes
    
    def set_changed_files(self, changed_files: List[str]) -> None:
        """Set list of changed files (for test control)."""
        self._changed_files = changed_files
