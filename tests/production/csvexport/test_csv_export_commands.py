"""
Tests for CSV export commands.
"""

import pytest
import sys
import csv
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
from io import StringIO

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))
# Add tests directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from jira_cleaner import run_remove_newlines
from csv_utils import run_extract_field_values
from jira_dates_eu import run as run_jira_dates_eu
from tests.fixtures.csv_scenarios import (
    create_csv_with_embedded_newlines,
    create_csv_for_field_extraction, 
    create_csv_with_iso_dates,
    create_newlines_removal_scenario,
    create_field_extraction_scenario,
    create_date_conversion_scenario
)
from tests.fixtures.base_fixtures import create_temp_csv_file, CSV_EMPTY


class TestCSVRemoveNewlinesCommand:
    """Test the csv-export remove-newlines command functionality."""
    
    def test_remove_newlines_from_csv_with_embedded_newlines(self):
        """Test newline removal from CSV fields with embedded newlines."""
        # Given: A CSV file containing fields with embedded newlines
        input_csv_file_with_embedded_newlines = create_temp_csv_file(create_csv_with_embedded_newlines())
        
        try:
            # When: User removes newlines from the input CSV file
            run_remove_newlines(input_csv_file_with_embedded_newlines, None)
            
            # Then: Output file should be created with newlines removed
            newlines_removed_output_file = input_csv_file_with_embedded_newlines.with_name(f"{input_csv_file_with_embedded_newlines.stem}-no-newlines.csv")
            assert newlines_removed_output_file.exists(), "Output file should be created"
            
            with open(newlines_removed_output_file, 'r', encoding='utf-8') as f:
                processed_content = f.read()
                assert "Task with newlines in summary" in processed_content
                assert "Description with multiple lines" in processed_content
                assert "Task with Windows newlines" in processed_content
                assert "Mixed line endings" in processed_content
                assert "\n" not in processed_content.split('\n')[1:], "Data rows should not contain newlines"
        finally:
            input_csv_file_with_embedded_newlines.unlink(missing_ok=True)
            newlines_removed_output_file.unlink(missing_ok=True)
    
    def test_remove_newlines_with_custom_output_path(self):
        """Test newline removal with custom output path."""
        # Given: A CSV file and custom output path
        input_csv_file_with_embedded_newlines = create_temp_csv_file(create_csv_with_embedded_newlines())
        custom_output_file_path = input_csv_file_with_embedded_newlines.parent / "custom_output.csv"
        
        try:
            # When: User removes newlines with the custom output path
            run_remove_newlines(input_csv_file_with_embedded_newlines, str(custom_output_file_path))
            
            # Then: Custom output file should be created
            assert custom_output_file_path.exists(), "Custom output file should be created"
            
            with open(custom_output_file_path, 'r', encoding='utf-8') as f:
                processed_content = f.read()
                assert "Task with newlines in summary" in processed_content
        finally:
            input_csv_file_with_embedded_newlines.unlink(missing_ok=True)
            custom_output_file_path.unlink(missing_ok=True)
    
    def test_remove_newlines_from_empty_csv(self):
        """Test newline removal from empty CSV file."""
        # Given: An empty CSV file
        input_empty_csv_file = create_temp_csv_file(CSV_EMPTY)
        
        try:
            # When: User removes newlines from the empty file
            run_remove_newlines(input_empty_csv_file, None)
            
            # Then: Output file should be created even for empty input
            newlines_removed_output_file = input_empty_csv_file.with_name(f"{input_empty_csv_file.stem}-no-newlines.csv")
            assert newlines_removed_output_file.exists(), "Output file should be created even for empty input"
        finally:
            input_empty_csv_file.unlink(missing_ok=True)
            newlines_removed_output_file.unlink(missing_ok=True)


class TestCSVExtractFieldValuesCommand:
    """Test the csv-export extract-to-comma-separated-list command functionality."""
    
    def test_extract_field_values_functionality(self):
        """Test field value extraction and file creation."""
        # Given: A CSV file with specific field data for extraction testing
        csv_for_field_extraction = create_temp_csv_file(create_csv_for_field_extraction())
        try:
            run_extract_field_values(csv_for_field_extraction, "Parent key", None)
            output_path = csv_for_field_extraction.with_name(f"{csv_for_field_extraction.stem}-parent-key.txt")
            assert output_path.exists(), "Parent key output file should be created"
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "(EPIC-1,EPIC-2)" in content
                assert "Parent key found=2" in content
        finally:
            csv_for_field_extraction.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)
        
        # Test different field types
        csv_with_status_and_priority = '''Issue key,Summary,Status,Priority
PROJ-1,Task 1,Done,High
PROJ-2,Task 2,In Progress,Medium
PROJ-3,Task 3,To Do,High
PROJ-4,Task 4,Done,Low'''
        
        csv_with_status_and_priority_file = create_temp_csv_file(csv_with_status_and_priority)
        try:
            # Test Status extraction
            run_extract_field_values(csv_with_status_and_priority_file, "Status", None)
            status_output = csv_with_status_and_priority_file.with_name(f"{csv_with_status_and_priority_file.stem}-status.txt")
            assert status_output.exists()
            
            with open(status_output, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "(Done,In Progress,To Do)" in content
                assert "Status found=3" in content
            
            # Test Priority extraction
            run_extract_field_values(csv_with_status_and_priority_file, "Priority", None)
            priority_output = csv_with_status_and_priority_file.with_name(f"{csv_with_status_and_priority_file.stem}-priority.txt")
            assert priority_output.exists()
            
            with open(priority_output, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "(High,Medium,Low)" in content
                assert "Priority found=3" in content
        finally:
            csv_with_status_and_priority_file.unlink(missing_ok=True)
            status_output.unlink(missing_ok=True)
            priority_output.unlink(missing_ok=True)
        
        # Test case insensitive matching
        csv_with_mixed_case_headers = '''Issue key,summary,parent key,STATUS
PROJ-1,Task 1,EPIC-1,Done
PROJ-2,Task 2,EPIC-1,In Progress'''
        
        csv_with_mixed_case_headers_file = create_temp_csv_file(csv_with_mixed_case_headers)
        try:
            run_extract_field_values(csv_with_mixed_case_headers_file, "Summary", None)  # Matches 'summary'
            run_extract_field_values(csv_with_mixed_case_headers_file, "Parent Key", None)  # Matches 'parent key'
            run_extract_field_values(csv_with_mixed_case_headers_file, "status", None)  # Matches 'STATUS'
            
            summary_output = csv_with_mixed_case_headers_file.with_name(f"{csv_with_mixed_case_headers_file.stem}-summary.txt")
            parent_output = csv_with_mixed_case_headers_file.with_name(f"{csv_with_mixed_case_headers_file.stem}-parent-key.txt")
            status_output = csv_with_mixed_case_headers_file.with_name(f"{csv_with_mixed_case_headers_file.stem}-status.txt")
            
            assert summary_output.exists()
            assert parent_output.exists()
            assert status_output.exists()
        finally:
            csv_with_mixed_case_headers_file.unlink(missing_ok=True)
            summary_output.unlink(missing_ok=True)
            parent_output.unlink(missing_ok=True)
            status_output.unlink(missing_ok=True)
        
        # Test nonexistent field
        csv_without_target_field = '''Issue key,Summary,Status
PROJ-1,Task 1,Done
PROJ-2,Task 2,In Progress'''
        
        csv_without_target_field_file = create_temp_csv_file(csv_without_target_field)
        try:
            with patch('builtins.print') as mock_print:
                run_extract_field_values(csv_without_target_field_file, "Nonexistent Field", None)
                mock_print.assert_called_with("Warning: 'Nonexistent Field' column not found in header or no values found.")
            
            output_path = csv_without_target_field_file.with_name(f"{csv_without_target_field_file.stem}-nonexistent-field.txt")
            assert not output_path.exists()
        finally:
            csv_without_target_field_file.unlink(missing_ok=True)


class TestCSVFixDatesEUCommand:
    """Test the csv-export fix-dates-eu command functionality."""
    
    def test_fix_dates_eu_functionality(self):
        """Test date conversion for European Excel format."""
        # Given: A CSV file containing date fields in ISO format
        csv_with_iso_dates = create_temp_csv_file(create_csv_with_iso_dates())
        try:
            run_jira_dates_eu(csv_with_iso_dates, None)
            output_path = csv_with_iso_dates.with_name(f"{csv_with_iso_dates.stem}-eu-dates.csv")
            assert output_path.exists(), "Output file should be created"
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "15/01/2024 10:30:00" in content
                assert "20/01/2024 14:45:00" in content
                assert "01/02/2024 09:15:00" in content
                assert "10/03/2024 11:00:00" in content
        finally:
            csv_with_iso_dates.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)
        
        # Test custom output path
        test_csv_content = '''Issue key,Created,Updated
PROJ-1,2024-01-15 10:30:00,2024-01-20 14:45:00'''
        
        input_file = create_temp_csv_file(test_csv_content)
        custom_output = input_file.parent / "custom_eu_dates.csv"
        try:
            run_jira_dates_eu(input_file, str(custom_output))
            assert custom_output.exists(), "Custom output file should be created"
            
            with open(custom_output, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "15/01/2024 10:30:00" in content
        finally:
            input_file.unlink(missing_ok=True)
            custom_output.unlink(missing_ok=True)
        
        # Test missing date columns
        test_csv_content = '''Issue key,Summary,Status
PROJ-1,Task 1,Done
PROJ-2,Task 2,In Progress'''
        
        input_file = create_temp_csv_file(test_csv_content)
        try:
            run_jira_dates_eu(input_file, None)
            output_path = input_file.with_name(f"{input_file.stem}-eu-dates.csv")
            assert output_path.exists(), "Output file should be created even without date columns"
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "PROJ-1,Task 1,Done" in content
                assert "PROJ-2,Task 2,In Progress" in content
        finally:
            input_file.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)
        
        # Test invalid dates
        test_csv_content = '''Issue key,Created,Updated
PROJ-1,invalid-date,2024-01-15 10:30:00
PROJ-2,2024-01-15 10:30:00,also-invalid
PROJ-3,2024-01-15 10:30:00,2024-01-20 14:45:00'''
        
        input_file = create_temp_csv_file(test_csv_content)
        try:
            run_jira_dates_eu(input_file, None)
            output_path = input_file.with_name(f"{input_file.stem}-eu-dates.csv")
            assert output_path.exists(), "Output file should be created"
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "invalid-date" in content
                assert "also-invalid" in content
                assert "15/01/2024 10:30:00" in content
                assert "20/01/2024 14:45:00" in content
        finally:
            input_file.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__])
