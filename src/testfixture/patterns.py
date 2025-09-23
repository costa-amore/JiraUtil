"""
Pattern definitions for test fixture management.

This module contains regex patterns and constants used for parsing
test fixture issue summaries and managing test fixture operations.
"""

import re
from typing import Optional, Tuple

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
