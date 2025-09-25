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
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from jira_cleaner import run_remove_newlines
from csv_utils import run_extract_field_values
from jira_dates_eu import run as run_jira_dates_eu
from .fixtures import (create_temp_csv_file, CSV_WITH_NEWLINES, CSV_FIELD_EXTRACTION, 
                       CSV_WITH_DATES, CSV_EMPTY)


class TestCSVRemoveNewlinesCommand:
    """Test the csv-export remove-newlines command functionality."""
    
    def test_remove_newlines_functionality(self):
        """Test newline removal from CSV fields."""
        # Test basic functionality
        input_file = create_temp_csv_file(CSV_WITH_NEWLINES)
        try:
            run_remove_newlines(input_file, None)
            output_path = input_file.with_name(f"{input_file.stem}-no-newlines.csv")
            assert output_path.exists(), "Output file should be created"
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Task with newlines in summary" in content
                assert "Description with multiple lines" in content
                assert "Task with Windows newlines" in content
                assert "Mixed line endings" in content
                assert "\n" not in content.split('\n')[1:], "Data rows should not contain newlines"
        finally:
            input_file.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)
        
        # Test custom output path
        input_file = create_temp_csv_file(CSV_WITH_NEWLINES)
        custom_output = input_file.parent / "custom_output.csv"
        try:
            run_remove_newlines(input_file, str(custom_output))
            assert custom_output.exists(), "Custom output file should be created"
            
            with open(custom_output, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Task with newlines in summary" in content
        finally:
            input_file.unlink(missing_ok=True)
            custom_output.unlink(missing_ok=True)
        
        # Test empty file
        input_file = create_temp_csv_file(CSV_EMPTY)
        try:
            run_remove_newlines(input_file, None)
            output_path = input_file.with_name(f"{input_file.stem}-no-newlines.csv")
            assert output_path.exists(), "Output file should be created even for empty input"
        finally:
            input_file.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)


class TestCSVExtractFieldValuesCommand:
    """Test the csv-export extract-to-comma-separated-list command functionality."""
    
    def test_extract_field_values_functionality(self):
        """Test field value extraction and file creation."""
        # Test basic functionality
        input_file = create_temp_csv_file(CSV_FIELD_EXTRACTION)
        try:
            run_extract_field_values(input_file, "Parent key", None)
            output_path = input_file.with_name(f"{input_file.stem}-parent-key.txt")
            assert output_path.exists(), "Parent key output file should be created"
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "(EPIC-1,EPIC-2)" in content
                assert "Parent key found=2" in content
        finally:
            input_file.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)
        
        # Test different field types
        test_csv_content = '''Issue key,Summary,Status,Priority
PROJ-1,Task 1,Done,High
PROJ-2,Task 2,In Progress,Medium
PROJ-3,Task 3,To Do,High
PROJ-4,Task 4,Done,Low'''
        
        input_file = create_temp_csv_file(test_csv_content)
        try:
            # Test Status extraction
            run_extract_field_values(input_file, "Status", None)
            status_output = input_file.with_name(f"{input_file.stem}-status.txt")
            assert status_output.exists()
            
            with open(status_output, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "(Done,In Progress,To Do)" in content
                assert "Status found=3" in content
            
            # Test Priority extraction
            run_extract_field_values(input_file, "Priority", None)
            priority_output = input_file.with_name(f"{input_file.stem}-priority.txt")
            assert priority_output.exists()
            
            with open(priority_output, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "(High,Medium,Low)" in content
                assert "Priority found=3" in content
        finally:
            input_file.unlink(missing_ok=True)
            status_output.unlink(missing_ok=True)
            priority_output.unlink(missing_ok=True)
        
        # Test case insensitive matching
        test_csv_content = '''Issue key,summary,parent key,STATUS
PROJ-1,Task 1,EPIC-1,Done
PROJ-2,Task 2,EPIC-1,In Progress'''
        
        input_file = create_temp_csv_file(test_csv_content)
        try:
            run_extract_field_values(input_file, "Summary", None)  # Matches 'summary'
            run_extract_field_values(input_file, "Parent Key", None)  # Matches 'parent key'
            run_extract_field_values(input_file, "status", None)  # Matches 'STATUS'
            
            summary_output = input_file.with_name(f"{input_file.stem}-summary.txt")
            parent_output = input_file.with_name(f"{input_file.stem}-parent-key.txt")
            status_output = input_file.with_name(f"{input_file.stem}-status.txt")
            
            assert summary_output.exists()
            assert parent_output.exists()
            assert status_output.exists()
        finally:
            input_file.unlink(missing_ok=True)
            summary_output.unlink(missing_ok=True)
            parent_output.unlink(missing_ok=True)
            status_output.unlink(missing_ok=True)
        
        # Test nonexistent field
        test_csv_content = '''Issue key,Summary,Status
PROJ-1,Task 1,Done
PROJ-2,Task 2,In Progress'''
        
        input_file = create_temp_csv_file(test_csv_content)
        try:
            with patch('builtins.print') as mock_print:
                run_extract_field_values(input_file, "Nonexistent Field", None)
                mock_print.assert_called_with("Warning: 'Nonexistent Field' column not found in header or no values found.")
            
            output_path = input_file.with_name(f"{input_file.stem}-nonexistent-field.txt")
            assert not output_path.exists()
        finally:
            input_file.unlink(missing_ok=True)


class TestCSVFixDatesEUCommand:
    """Test the csv-export fix-dates-eu command functionality."""
    
    def test_fix_dates_eu_functionality(self):
        """Test date conversion for European Excel format."""
        # Test basic functionality
        input_file = create_temp_csv_file(CSV_WITH_DATES)
        try:
            run_jira_dates_eu(input_file, None)
            output_path = input_file.with_name(f"{input_file.stem}-eu-dates.csv")
            assert output_path.exists(), "Output file should be created"
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "15/01/2024 10:30:00" in content
                assert "20/01/2024 14:45:00" in content
                assert "01/02/2024 09:15:00" in content
                assert "10/03/2024 11:00:00" in content
        finally:
            input_file.unlink(missing_ok=True)
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
