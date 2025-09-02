import pytest
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from jira_parent_extractor import (
	find_parent_key_index,
	extract_parent_keys_from_rows,
	format_parent_keys_text
)


class TestFindParentKeyIndex:
	"""Test the find_parent_key_index function."""
	
	def test_exact_match(self):
		"""Test finding Parent key with exact match."""
		header = ["Issue key", "Summary", "Parent key", "Status"]
		assert find_parent_key_index(header) == 2
	
	def test_case_insensitive_match(self):
		"""Test finding parent key with case insensitive match."""
		header = ["Issue key", "Summary", "parent key", "Status"]
		assert find_parent_key_index(header) == 2
	
	def test_whitespace_trimmed_match(self):
		"""Test finding parent key with whitespace trimmed."""
		header = ["Issue key", "Summary", " Parent key ", "Status"]
		assert find_parent_key_index(header) == 2
	
	def test_not_found(self):
		"""Test when Parent key column is not found."""
		header = ["Issue key", "Summary", "Status"]
		assert find_parent_key_index(header) is None
	
	def test_empty_header(self):
		"""Test with empty header."""
		header = []
		assert find_parent_key_index(header) is None


class TestExtractParentKeysFromRows:
	"""Test the extract_parent_keys_from_rows function."""
	
	def test_extract_parent_keys_basic(self):
		"""Test basic parent key extraction."""
		rows = [
			["Issue key", "Summary", "Parent key", "Status"],
			["PROJ-1", "Task 1", "EPIC-1", "Done"],
			["PROJ-2", "Task 2", "EPIC-1", "In Progress"],
			["PROJ-3", "Task 3", "EPIC-2", "To Do"]
		]
		parent_keys, count = extract_parent_keys_from_rows(rows)
		assert parent_keys == ["EPIC-1", "EPIC-2"]
		assert count == 2
	
	def test_extract_parent_keys_with_duplicates(self):
		"""Test parent key extraction with duplicates."""
		rows = [
			["Issue key", "Summary", "Parent key", "Status"],
			["PROJ-1", "Task 1", "EPIC-1", "Done"],
			["PROJ-2", "Task 2", "EPIC-1", "In Progress"],
			["PROJ-3", "Task 3", "EPIC-1", "To Do"],
			["PROJ-4", "Task 4", "EPIC-2", "Done"]
		]
		parent_keys, count = extract_parent_keys_from_rows(rows)
		assert parent_keys == ["EPIC-1", "EPIC-2"]
		assert count == 2
	
	def test_extract_parent_keys_with_empty_values(self):
		"""Test parent key extraction with empty values."""
		rows = [
			["Issue key", "Summary", "Parent key", "Status"],
			["PROJ-1", "Task 1", "EPIC-1", "Done"],
			["PROJ-2", "Task 2", "", "In Progress"],
			["PROJ-3", "Task 3", "EPIC-2", "To Do"],
			["PROJ-4", "Task 4", None, "Done"]
		]
		parent_keys, count = extract_parent_keys_from_rows(rows)
		assert parent_keys == ["EPIC-1", "EPIC-2"]
		assert count == 2
	
	def test_no_parent_key_column(self):
		"""Test when Parent key column doesn't exist."""
		rows = [
			["Issue key", "Summary", "Status"],
			["PROJ-1", "Task 1", "Done"],
			["PROJ-2", "Task 2", "In Progress"]
		]
		parent_keys, count = extract_parent_keys_from_rows(rows)
		assert parent_keys == []
		assert count == 0
	
	def test_empty_rows(self):
		"""Test with empty rows."""
		rows = []
		parent_keys, count = extract_parent_keys_from_rows(rows)
		assert parent_keys == []
		assert count == 0
	
	def test_header_only(self):
		"""Test with header only, no data rows."""
		rows = [
			["Issue key", "Summary", "Parent key", "Status"]
		]
		parent_keys, count = extract_parent_keys_from_rows(rows)
		assert parent_keys == []
		assert count == 0


class TestFormatParentKeysText:
	"""Test the format_parent_keys_text function."""
	
	def test_format_single_parent_key(self):
		"""Test formatting a single parent key."""
		parent_keys = ["EPIC-1"]
		result = format_parent_keys_text(parent_keys)
		expected = "(EPIC-1)\nparents found=1\n"
		assert result == expected
	
	def test_format_multiple_parent_keys(self):
		"""Test formatting multiple parent keys."""
		parent_keys = ["EPIC-1", "EPIC-2", "EPIC-3"]
		result = format_parent_keys_text(parent_keys)
		expected = "(EPIC-1,EPIC-2,EPIC-3)\nparents found=3\n"
		assert result == expected
	
	def test_format_empty_parent_keys(self):
		"""Test formatting empty parent keys list."""
		parent_keys = []
		result = format_parent_keys_text(parent_keys)
		expected = "()\nparents found=0\n"
		assert result == expected


if __name__ == "__main__":
	pytest.main([__file__])
