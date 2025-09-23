"""
Field name matching functionality for CSV processing.

This module handles finding and matching field names in CSV headers
with various matching strategies.
"""

from typing import List


def find_field_index(header: List[str], field_name: str) -> int | None:
    """Find the index of the specified field column in the CSV header."""
    # Try exact match first
    try:
        return header.index(field_name)
    except ValueError:
        pass
    # Fall back to case-insensitive and trimmed comparison
    normalized = [h.strip().lower() for h in header]
    field_name_lower = field_name.strip().lower()
    for idx, name in enumerate(normalized):
        if name == field_name_lower:
            return idx
    return None
