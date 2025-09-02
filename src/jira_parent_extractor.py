import csv
from pathlib import Path
from typing import List, Tuple


def find_parent_key_index(header: List[str]) -> int | None:
	"""Find the index of the 'Parent key' column in the CSV header."""
	# Try exact match first
	try:
		return header.index("Parent key")
	except ValueError:
		pass
	# Fall back to case-insensitive and trimmed comparison
	normalized = [h.strip().lower() for h in header]
	for idx, name in enumerate(normalized):
		if name == "parent key":
			return idx
	return None


def extract_parent_keys_from_rows(rows: List[List[str]]) -> Tuple[List[str], int]:
	"""Extract parent keys from CSV rows and return unique list with count."""
	if not rows:
		return [], 0
	
	header = rows[0]
	parent_idx = find_parent_key_index(header)
	
	if parent_idx is None:
		return [], 0
	
	parent_keys: List[str] = []
	
	# Extract parent key values from data rows (skip header)
	for row in rows[1:]:
		if parent_idx < len(row):
			value = row[parent_idx]
			if value:
				parent_keys.append(value)

	# Deduplicate while preserving order
	seen = set()
	ordered_unique: List[str] = []
	for key in parent_keys:
		if key not in seen:
			seen.add(key)
			ordered_unique.append(key)
	
	return ordered_unique, len(ordered_unique)


def extract_parent_keys_from_csv(input_path: Path) -> Tuple[List[str], int]:
	"""Extract parent keys from CSV file and return unique list with count."""
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
		return extract_parent_keys_from_rows(rows)


def format_parent_keys_text(parent_keys: List[str]) -> str:
	"""Format parent keys as text with count."""
	count = len(parent_keys)
	joined = ",".join(parent_keys)
	# Enclose in parentheses and append a count line
	return f"({joined})\nparents found={count}\n"


def write_parent_file_for_input(input_path: Path, parent_keys: List[str]) -> Tuple[Path, int]:
	"""Write parent keys to a text file."""
	parent_text = format_parent_keys_text(parent_keys)
	parent_file = input_path.with_name(f"{input_path.stem}-parents.txt")
	with open(parent_file, 'w', encoding='utf-8', newline='') as f:
		f.write(parent_text)
	return parent_file, len(parent_keys)


def run_extract_parent_keys(input_path: Path, output: str | None) -> None:
	"""Extract parent keys from CSV and write to text file."""
	parent_keys, count = extract_parent_keys_from_csv(input_path)
	if count == 0:
		print("Warning: 'Parent key' column not found in header or no parent keys found.")
	else:
		parent_file, _ = write_parent_file_for_input(input_path, parent_keys)
		print(f"Found {count} unique parent keys. Written to {parent_file}")
