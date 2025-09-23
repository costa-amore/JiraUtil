import pytest
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from csv_utils.field_matcher import find_field_index
from csv_utils.field_extractor import (
	extract_field_values_from_rows,
	format_field_values_text
)


class TestFindFieldIndex:
	"""Test the find_field_index function."""
	
	def test_exact_match(self):
		"""Test finding field with exact match."""
		header = ["Issue key", "Summary", "Parent key", "Status"]
		assert find_field_index(header, "Parent key") == 2
		assert find_field_index(header, "Status") == 3
	
	def test_case_insensitive_match(self):
		"""Test finding field with case insensitive match."""
		header = ["Issue key", "Summary", "parent key", "Status"]
		assert find_field_index(header, "Parent key") == 2
		assert find_field_index(header, "status") == 3
	
	def test_whitespace_trimmed_match(self):
		"""Test finding field with whitespace trimmed."""
		header = ["Issue key", "Summary", " Parent key ", "Status"]
		assert find_field_index(header, "Parent key") == 2
		assert find_field_index(header, " Status ") == 3
	
	def test_not_found(self):
		"""Test when field column is not found."""
		header = ["Issue key", "Summary", "Status"]
		assert find_field_index(header, "Parent key") is None
		assert find_field_index(header, "Assignee") is None
	
	def test_empty_header(self):
		"""Test with empty header."""
		header = []
		assert find_field_index(header, "Parent key") is None


class TestExtractFieldValuesFromRows:
	"""Test the extract_field_values_from_rows function."""
	
	def test_extract_field_values_basic(self):
		"""Test basic field value extraction."""
		rows = [
			["Issue key", "Summary", "Parent key", "Status"],
			["PROJ-1", "Task 1", "EPIC-1", "Done"],
			["PROJ-2", "Task 2", "EPIC-1", "In Progress"],
			["PROJ-3", "Task 3", "EPIC-2", "To Do"]
		]
		field_values, count = extract_field_values_from_rows(rows, "Parent key")
		assert field_values == ["EPIC-1", "EPIC-2"]
		assert count == 2
		
		# Test extracting Status field
		status_values, status_count = extract_field_values_from_rows(rows, "Status")
		assert status_values == ["Done", "In Progress", "To Do"]
		assert status_count == 3
	
	def test_extract_field_values_with_duplicates(self):
		"""Test field value extraction with duplicates."""
		rows = [
			["Issue key", "Summary", "Parent key", "Status"],
			["PROJ-1", "Task 1", "EPIC-1", "Done"],
			["PROJ-2", "Task 2", "EPIC-1", "In Progress"],
			["PROJ-3", "Task 3", "EPIC-1", "To Do"],
			["PROJ-4", "Task 4", "EPIC-2", "Done"]
		]
		field_values, count = extract_field_values_from_rows(rows, "Parent key")
		assert field_values == ["EPIC-1", "EPIC-2"]
		assert count == 2
		
		# Test Status field with duplicates
		status_values, status_count = extract_field_values_from_rows(rows, "Status")
		assert status_values == ["Done", "In Progress", "To Do"]
		assert status_count == 3
	
	def test_extract_field_values_with_empty_values(self):
		"""Test field value extraction with empty values."""
		rows = [
			["Issue key", "Summary", "Parent key", "Status"],
			["PROJ-1", "Task 1", "EPIC-1", "Done"],
			["PROJ-2", "Task 2", "", "In Progress"],
			["PROJ-3", "Task 3", "EPIC-2", "To Do"],
			["PROJ-4", "Task 4", None, "Done"]
		]
		field_values, count = extract_field_values_from_rows(rows, "Parent key")
		assert field_values == ["EPIC-1", "EPIC-2"]
		assert count == 2
	
	def test_no_field_column(self):
		"""Test when field column doesn't exist."""
		rows = [
			["Issue key", "Summary", "Status"],
			["PROJ-1", "Task 1", "Done"],
			["PROJ-2", "Task 2", "In Progress"]
		]
		field_values, count = extract_field_values_from_rows(rows, "Parent key")
		assert field_values == []
		assert count == 0
	
	def test_empty_rows(self):
		"""Test with empty rows."""
		rows = []
		field_values, count = extract_field_values_from_rows(rows, "Parent key")
		assert field_values == []
		assert count == 0
	
	def test_header_only(self):
		"""Test with header only, no data rows."""
		rows = [
			["Issue key", "Summary", "Parent key", "Status"]
		]
		field_values, count = extract_field_values_from_rows(rows, "Parent key")
		assert field_values == []
		assert count == 0


class TestFormatFieldValuesText:
	"""Test the format_field_values_text function."""
	
	def test_format_single_field_value(self):
		"""Test formatting a single field value."""
		field_values = ["EPIC-1"]
		result = format_field_values_text(field_values, "Parent key")
		expected = "(EPIC-1)\nParent key found=1\n"
		assert result == expected
	
	def test_format_multiple_field_values(self):
		"""Test formatting multiple field values."""
		field_values = ["EPIC-1", "EPIC-2", "EPIC-3"]
		result = format_field_values_text(field_values, "Parent key")
		expected = "(EPIC-1,EPIC-2,EPIC-3)\nParent key found=3\n"
		assert result == expected
	
	def test_format_empty_field_values(self):
		"""Test formatting empty field values list."""
		field_values = []
		result = format_field_values_text(field_values, "Parent key")
		expected = "()\nParent key found=0\n"
		assert result == expected
	
	def test_format_different_field_names(self):
		"""Test formatting with different field names."""
		field_values = ["Done", "In Progress"]
		result = format_field_values_text(field_values, "Status")
		expected = "(Done,In Progress)\nStatus found=2\n"
		assert result == expected


if __name__ == "__main__":
	pytest.main([__file__])
