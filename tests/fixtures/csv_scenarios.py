"""
CSV processing scenarios for testing CSV export commands.

This module contains complete test scenarios that group CSV test data
with expected results for CSV processing operations.
"""

from .base_fixtures import create_temp_csv_file, create_mock_manager_with_expected_results


def create_csv_with_embedded_newlines():
    """Create CSV content with various newline formats for testing newline removal."""
    return '''Issue key,Summary,Description,Status
PROJ-1,"Task with newlines
in summary","Description with
multiple lines",Done
PROJ-2,"Normal task","Single line description",In Progress
PROJ-3,"Task with\r\nWindows newlines","Mixed\r\nline endings",To Do'''


def create_csv_for_field_extraction():
    """Create CSV content with structured data for testing field value extraction."""
    return '''Issue key,Summary,Parent key,Status,Assignee
PROJ-1,Task 1,EPIC-1,Done,John Doe
PROJ-2,Task 2,EPIC-1,In Progress,Jane Smith
PROJ-3,Task 3,EPIC-2,To Do,John Doe
PROJ-4,Task 4,EPIC-1,Done,Bob Wilson'''


def create_csv_with_iso_dates():
    """Create CSV content with ISO date formats for testing European date conversion."""
    return '''Issue key,Summary,Created,Updated,Status
PROJ-1,Task 1,2024-01-15 10:30:00,2024-01-20 14:45:00,Done
PROJ-2,Task 2,2024-02-01 09:15:00,2024-02-05 16:20:00,In Progress
PROJ-3,Task 3,2024-03-10 11:00:00,2024-03-10 11:00:00,To Do'''


def create_newlines_removal_scenario():
    """Create a complete scenario for testing newline removal."""
    # Test data: CSV with embedded newlines
    csv_content = create_csv_with_embedded_newlines()
    csv_file = create_temp_csv_file(csv_content)
    
    # Expected results: File should be processed successfully
    return {
        'input_file': csv_file,
        'expected_output_exists': True,
        'expected_content_checks': [
            "Task with newlines in summary",
            "Description with multiple lines", 
            "Task with Windows newlines",
            "Mixed line endings"
        ],
        'expected_no_newlines_in_data': True
    }


def create_field_extraction_scenario():
    """Create a complete scenario for testing field value extraction."""
    # Test data: CSV with structured field data
    csv_content = create_csv_for_field_extraction()
    csv_file = create_temp_csv_file(csv_content)
    
    # Expected results: Should extract unique values correctly
    return {
        'input_file': csv_file,
        'field_name': 'Parent key',
        'expected_output_exists': True,
        'expected_unique_values': ['EPIC-1', 'EPIC-2'],
        'expected_count': 2
    }


def create_date_conversion_scenario():
    """Create a complete scenario for testing date conversion."""
    # Test data: CSV with ISO dates
    csv_content = create_csv_with_iso_dates()
    csv_file = create_temp_csv_file(csv_content)
    
    # Expected results: Should convert to European format
    return {
        'input_file': csv_file,
        'expected_output_exists': True,
        'expected_eu_dates': [
            "15/01/2024 10:30:00",
            "20/01/2024 14:45:00", 
            "01/02/2024 09:15:00",
            "10/03/2024 11:00:00"
        ]
    }
