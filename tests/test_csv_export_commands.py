"""
Functional tests for CSV export commands.

This module tests the complete CSV export functionality including:
- remove-newlines command
- extract-to-comma-separated-list command  
- fix-dates-eu command
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


class TestCSVRemoveNewlinesCommand:
    """Test the csv-export remove-newlines command functionality."""
    
    def test_remove_newlines_basic_functionality(self):
        """Test basic newline removal from CSV fields."""
        # Create test CSV content with newlines
        test_csv_content = '''Issue key,Summary,Description,Status
PROJ-1,"Task with newlines
in summary","Description with
multiple lines",Done
PROJ-2,"Normal task","Single line description",In Progress
PROJ-3,"Task with\r\nWindows newlines","Mixed\r\nline endings",To Do'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as input_file:
            input_file.write(test_csv_content)
            input_file_path = Path(input_file.name)
        
        try:
            # Run the command
            run_remove_newlines(input_file_path, None)
            
            # Check output file was created
            output_path = input_file_path.with_name(f"{input_file_path.stem}-no-newlines.csv")
            assert output_path.exists(), "Output file should be created"
            
            # Verify content
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Task with newlines in summary" in content, "Newlines should be replaced with spaces"
                assert "Description with multiple lines" in content, "Multiple line descriptions should be cleaned"
                assert "Task with Windows newlines" in content, "Windows newlines should be cleaned"
                assert "Mixed line endings" in content, "Mixed line endings should be cleaned"
                assert "\n" not in content.split('\n')[1:], "Data rows should not contain newlines"
                
        finally:
            # Cleanup
            input_file_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)
    
    def test_remove_newlines_with_custom_output_path(self):
        """Test newline removal with custom output path."""
        test_csv_content = '''Issue key,Summary
PROJ-1,"Task with
newlines"'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as input_file:
            input_file.write(test_csv_content)
            input_file_path = Path(input_file.name)
        
        custom_output = input_file_path.parent / "custom_output.csv"
        
        try:
            run_remove_newlines(input_file_path, str(custom_output))
            assert custom_output.exists(), "Custom output file should be created"
            
            with open(custom_output, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Task with newlines" in content, "Newlines should be cleaned in custom output"
                
        finally:
            input_file_path.unlink(missing_ok=True)
            custom_output.unlink(missing_ok=True)
    
    def test_remove_newlines_handles_empty_file(self):
        """Test newline removal with empty CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as input_file:
            input_file.write("")
            input_file_path = Path(input_file.name)
        
        try:
            run_remove_newlines(input_file_path, None)
            output_path = input_file_path.with_name(f"{input_file_path.stem}-no-newlines.csv")
            assert output_path.exists(), "Output file should be created even for empty input"
            
        finally:
            input_file_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)


class TestCSVExtractFieldValuesCommand:
    """Test the csv-export extract-to-comma-separated-list command functionality."""
    
    def test_extract_field_values_basic_functionality(self):
        """Test basic field value extraction and file creation."""
        test_csv_content = '''Issue key,Summary,Parent key,Status,Assignee
PROJ-1,Task 1,EPIC-1,Done,John Doe
PROJ-2,Task 2,EPIC-1,In Progress,Jane Smith
PROJ-3,Task 3,EPIC-2,To Do,John Doe
PROJ-4,Task 4,EPIC-1,Done,Bob Wilson'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as input_file:
            input_file.write(test_csv_content)
            input_file_path = Path(input_file.name)
        
        try:
            # Test Parent key extraction
            run_extract_field_values(input_file_path, "Parent key", None)
            
            # Check output file was created
            output_path = input_file_path.with_name(f"{input_file_path.stem}-parent-key.txt")
            assert output_path.exists(), "Parent key output file should be created"
            
            # Verify content
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "(EPIC-1,EPIC-2)" in content, "Should contain unique parent keys"
                assert "Parent key found=2" in content, "Should show correct count"
                
        finally:
            input_file_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)
    
    def test_extract_field_values_different_fields(self):
        """Test extraction of different field types."""
        test_csv_content = '''Issue key,Summary,Status,Priority
PROJ-1,Task 1,Done,High
PROJ-2,Task 2,In Progress,Medium
PROJ-3,Task 3,To Do,High
PROJ-4,Task 4,Done,Low'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as input_file:
            input_file.write(test_csv_content)
            input_file_path = Path(input_file.name)
        
        try:
            # Test Status extraction
            run_extract_field_values(input_file_path, "Status", None)
            status_output = input_file_path.with_name(f"{input_file_path.stem}-status.txt")
            assert status_output.exists(), "Status output file should be created"
            
            with open(status_output, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "(Done,In Progress,To Do)" in content, "Should contain unique statuses"
                assert "Status found=3" in content, "Should show correct count"
            
            # Test Priority extraction
            run_extract_field_values(input_file_path, "Priority", None)
            priority_output = input_file_path.with_name(f"{input_file_path.stem}-priority.txt")
            assert priority_output.exists(), "Priority output file should be created"
            
            with open(priority_output, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "(High,Medium,Low)" in content, "Should contain unique priorities"
                assert "Priority found=3" in content, "Should show correct count"
                
        finally:
            input_file_path.unlink(missing_ok=True)
            status_output.unlink(missing_ok=True)
            priority_output.unlink(missing_ok=True)
    
    def test_extract_field_values_case_insensitive_matching(self):
        """Test field name matching is case insensitive."""
        test_csv_content = '''Issue key,summary,parent key,STATUS
PROJ-1,Task 1,EPIC-1,Done
PROJ-2,Task 2,EPIC-1,In Progress'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as input_file:
            input_file.write(test_csv_content)
            input_file_path = Path(input_file.name)
        
        try:
            # Test case insensitive matching
            run_extract_field_values(input_file_path, "Summary", None)  # Matches 'summary'
            run_extract_field_values(input_file_path, "Parent Key", None)  # Matches 'parent key'
            run_extract_field_values(input_file_path, "status", None)  # Matches 'STATUS'
            
            # Verify files were created
            summary_output = input_file_path.with_name(f"{input_file_path.stem}-summary.txt")
            parent_output = input_file_path.with_name(f"{input_file_path.stem}-parent-key.txt")
            status_output = input_file_path.with_name(f"{input_file_path.stem}-status.txt")
            
            assert summary_output.exists(), "Summary file should be created"
            assert parent_output.exists(), "Parent key file should be created"
            assert status_output.exists(), "Status file should be created"
            
        finally:
            input_file_path.unlink(missing_ok=True)
            summary_output.unlink(missing_ok=True)
            parent_output.unlink(missing_ok=True)
            status_output.unlink(missing_ok=True)
    
    def test_extract_field_values_nonexistent_field(self):
        """Test behavior when field doesn't exist."""
        test_csv_content = '''Issue key,Summary,Status
PROJ-1,Task 1,Done
PROJ-2,Task 2,In Progress'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as input_file:
            input_file.write(test_csv_content)
            input_file_path = Path(input_file.name)
        
        try:
            # This should not create an output file and should print warning
            with patch('builtins.print') as mock_print:
                run_extract_field_values(input_file_path, "Nonexistent Field", None)
                mock_print.assert_called_with("Warning: 'Nonexistent Field' column not found in header or no values found.")
            
            # Verify no output file was created
            output_path = input_file_path.with_name(f"{input_file_path.stem}-nonexistent-field.txt")
            assert not output_path.exists(), "No output file should be created for nonexistent field"
            
        finally:
            input_file_path.unlink(missing_ok=True)


class TestCSVFixDatesEUCommand:
    """Test the csv-export fix-dates-eu command functionality."""
    
    def test_fix_dates_eu_basic_functionality(self):
        """Test basic date conversion for European Excel format."""
        test_csv_content = '''Issue key,Summary,Created,Updated,Status
PROJ-1,Task 1,2024-01-15 10:30:00,2024-01-20 14:45:00,Done
PROJ-2,Task 2,2024-02-01 09:15:00,2024-02-05 16:20:00,In Progress
PROJ-3,Task 3,2024-03-10 11:00:00,2024-03-10 11:00:00,To Do'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as input_file:
            input_file.write(test_csv_content)
            input_file_path = Path(input_file.name)
        
        try:
            # Run the command
            run_jira_dates_eu(input_file_path, None)
            
            # Check output file was created
            output_path = input_file_path.with_name(f"{input_file_path.stem}-eu-dates.csv")
            assert output_path.exists(), "Output file should be created"
            
            # Verify content
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "15/01/2024 10:30:00" in content, "Created date should be in EU format"
                assert "20/01/2024 14:45:00" in content, "Updated date should be in EU format"
                assert "01/02/2024 09:15:00" in content, "February date should be in EU format"
                assert "10/03/2024 11:00:00" in content, "March date should be in EU format"
                
        finally:
            input_file_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)
    
    def test_fix_dates_eu_with_custom_output_path(self):
        """Test date conversion with custom output path."""
        test_csv_content = '''Issue key,Created,Updated
PROJ-1,2024-01-15 10:30:00,2024-01-20 14:45:00'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as input_file:
            input_file.write(test_csv_content)
            input_file_path = Path(input_file.name)
        
        custom_output = input_file_path.parent / "custom_eu_dates.csv"
        
        try:
            run_jira_dates_eu(input_file_path, str(custom_output))
            assert custom_output.exists(), "Custom output file should be created"
            
            with open(custom_output, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "15/01/2024 10:30:00" in content, "Date should be in EU format in custom output"
                
        finally:
            input_file_path.unlink(missing_ok=True)
            custom_output.unlink(missing_ok=True)
    
    def test_fix_dates_eu_handles_missing_date_columns(self):
        """Test behavior when Created or Updated columns are missing."""
        test_csv_content = '''Issue key,Summary,Status
PROJ-1,Task 1,Done
PROJ-2,Task 2,In Progress'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as input_file:
            input_file.write(test_csv_content)
            input_file_path = Path(input_file.name)
        
        try:
            run_jira_dates_eu(input_file_path, None)
            output_path = input_file_path.with_name(f"{input_file_path.stem}-eu-dates.csv")
            assert output_path.exists(), "Output file should be created even without date columns"
            
            # Verify original content is preserved
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "PROJ-1,Task 1,Done" in content, "Original content should be preserved"
                assert "PROJ-2,Task 2,In Progress" in content, "Original content should be preserved"
                
        finally:
            input_file_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)
    
    def test_fix_dates_eu_handles_invalid_dates(self):
        """Test behavior with invalid date formats."""
        test_csv_content = '''Issue key,Created,Updated
PROJ-1,invalid-date,2024-01-15 10:30:00
PROJ-2,2024-01-15 10:30:00,also-invalid
PROJ-3,2024-01-15 10:30:00,2024-01-20 14:45:00'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as input_file:
            input_file.write(test_csv_content)
            input_file_path = Path(input_file.name)
        
        try:
            run_jira_dates_eu(input_file_path, None)
            output_path = input_file_path.with_name(f"{input_file_path.stem}-eu-dates.csv")
            assert output_path.exists(), "Output file should be created"
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "invalid-date" in content, "Invalid dates should be left unchanged"
                assert "also-invalid" in content, "Invalid dates should be left unchanged"
                assert "15/01/2024 10:30:00" in content, "Valid dates should be converted"
                assert "20/01/2024 14:45:00" in content, "Valid dates should be converted"
                
        finally:
            input_file_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__])
