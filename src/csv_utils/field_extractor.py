"""
Field value extraction functionality for CSV processing.

This module handles extracting field values from CSV files and
formatting them for output.
"""

import csv
from pathlib import Path
from typing import List, Tuple
from .field_matcher import find_field_index


def extract_field_values_from_rows(rows: List[List[str]], field_name: str) -> Tuple[List[str], int]:
    """Extract field values from CSV rows and return unique list with count."""
    if not rows:
        return [], 0
    
    header = rows[0]
    field_idx = find_field_index(header, field_name)
    
    if field_idx is None:
        return [], 0
    
    field_values: List[str] = []
    
    # Extract field values from data rows (skip header)
    for row in rows[1:]:
        if field_idx < len(row):
            value = row[field_idx]
            if value:
                field_values.append(value)

    # Deduplicate while preserving order
    seen = set()
    ordered_unique: List[str] = []
    for value in field_values:
        if value not in seen:
            seen.add(value)
            ordered_unique.append(value)
    
    return ordered_unique, len(ordered_unique)


def extract_field_values_from_csv(input_path: Path, field_name: str) -> Tuple[List[str], int]:
    """Extract field values from CSV file and return unique list with count."""
    with open(input_path, 'r', newline='', encoding='utf-8-sig') as infile:
        reader = csv.reader(
            infile,
            delimiter=',',
            quotechar='"',
            doublequote=True,
            skipinitialspace=False,
            strict=False,
        )
        
        # Read all rows
        rows = list(reader)
        return extract_field_values_from_rows(rows, field_name)


def format_field_values_text(field_values: List[str], field_name: str) -> str:
    """Format field values as text with count."""
    count = len(field_values)
    joined = ",".join(field_values)
    # Enclose in parentheses and append a count line
    return f"({joined})\n{field_name} found={count}\n"


def write_field_values_file_for_input(input_path: Path, field_values: List[str], field_name: str) -> Tuple[Path, int]:
    """Write field values to a text file."""
    field_text = format_field_values_text(field_values, field_name)
    # Create safe filename from field name
    safe_field_name = "".join(c for c in field_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_field_name = safe_field_name.replace(' ', '-').lower()
    field_file = input_path.with_name(f"{input_path.stem}-{safe_field_name}.txt")
    with open(field_file, 'w', encoding='utf-8', newline='') as f:
        f.write(field_text)
    return field_file, len(field_values)


def run_extract_field_values(input_path: Path, field_name: str, output: str | None) -> None:
    """Extract field values from CSV and write to text file."""
    field_values, count = extract_field_values_from_csv(input_path, field_name)
    if count == 0:
        print(f"Warning: '{field_name}' column not found in header or no values found.")
    else:
        field_file, _ = write_field_values_file_for_input(input_path, field_values, field_name)
        print(f"Found {count} unique {field_name} values. Written to {field_file}")


# Legacy function for backward compatibility
def run_extract_parent_keys(input_path: Path, output: str | None) -> None:
    """Legacy function that extracts parent keys. Use run_extract_field_values instead."""
    run_extract_field_values(input_path, "Parent key", output)
