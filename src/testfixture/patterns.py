"""
Pattern definitions for test fixture management.

This module contains regex patterns and constants used for parsing
test fixture issue summaries and managing test fixture operations.
"""

import re
from typing import Optional, Tuple

# Pattern matching for test fixture issue summaries
START_STATE_PATTERN = r"(?:starting in|I was in)"
EXPECTED_STATE_PATTERN = r"expected to be in"
SUMMARY_PATTERN = rf"^(.*?)(?:{START_STATE_PATTERN}) (.+?) - {EXPECTED_STATE_PATTERN} (.+)"

# Default label for test fixture issues (used to verify automation rules)
DEFAULT_TEST_FIXTURE_LABEL = "rule-testing"


# Public functions (sorted alphabetically)
def extract_context_from_summary(summary: str) -> Optional[str]:
    result = _parse_summary_groups(summary)
    
    if result:
        context = result[0]  # Group 1 is context
        # Remove trailing " - " if present
        if context.endswith(" - "):
            context = context[:-3]
        # Return context only if it's not empty and not just the start state pattern
        if context and not re.match(rf"^{START_STATE_PATTERN}$", context, re.IGNORECASE):
            return context
    
    return None


def extract_statuses_from_summary(summary: str) -> Optional[Tuple[str, str]]:
    result = _parse_summary_groups(summary)
    return (result[1], result[2]) if result else None


# Private functions (sorted alphabetically)
def _parse_summary_groups(summary: str) -> Optional[Tuple[str, str, str]]:
    match = re.search(SUMMARY_PATTERN, summary, re.IGNORECASE)
    
    if match:
        context = match.group(1).strip()  # Group 1 is context
        status1 = match.group(2).strip()  # Group 2 is status1
        status2 = match.group(3).strip()  # Group 3 is status2
        return (context, status1, status2)
    
    return None
