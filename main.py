import argparse
import csv
import re
from pathlib import Path
from typing import List, Tuple

# Characters that can cause Excel to interpret a new row when present inside fields
# Includes CR, LF, Unicode line/paragraph separators, and Next Line.
LINE_BREAK_PATTERN = re.compile(r"[\r\n\u2028\u2029\u0085]+")


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Clean Jira CSV by removing embedded line breaks inside fields.")
	parser.add_argument("input", help="Path to the input Jira CSV file")
	parser.add_argument("--output", "-o", help="Optional output file path. If omitted, a -cleaned.csv file is created next to the input.")
	return parser.parse_args()


def build_output_path(input_path: Path, explicit_output: str | None) -> Path:
	if explicit_output:
		return Path(explicit_output)
	# Default: same folder, base name with -cleaned.csv
	stem = input_path.stem
	# Always use .csv for output
	return input_path.with_name(f"{stem}-cleaned.csv")


def find_parent_key_index(header: List[str]) -> int | None:
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


def clean_csv(input_path: Path, output_path: Path) -> Tuple[int | None, List[str]]:
	parent_keys: List[str] = []
	with open(input_path, 'r', newline='', encoding='utf-8-sig') as infile, \
		open(output_path, 'w', newline='', encoding='utf-8') as outfile:
		# Explicit Jira/Excel-style CSV settings (comma delimiter, double quotes)
		reader = csv.reader(
			infile,
			delimiter=',',
			quotechar='"',
			doublequote=True,
			skipinitialspace=False,
			strict=False,
		)
		writer = csv.writer(
			outfile,
			delimiter=',',
			quotechar='"',
			quoting=csv.QUOTE_MINIMAL,
			lineterminator='\r\n',
			escapechar='\\',
		)

		# Read header
		header = next(reader, None)
		if header is not None:
			writer.writerow(header)
			parent_idx = find_parent_key_index(header)
		else:
			parent_idx = None

		# Sanitize each field and track Parent key values
		for row in reader:
			cleaned_row = []
			for field in row:
				# Replace any line-breaking characters with a single space
				cleaned_field = LINE_BREAK_PATTERN.sub(' ', field)
				# Optionally collapse repeated spaces created by replacements
				cleaned_field = re.sub(r'\s{2,}', ' ', cleaned_field).strip()
				cleaned_row.append(cleaned_field)
			# Collect parent key if available
			if parent_idx is not None and parent_idx < len(cleaned_row):
				value = cleaned_row[parent_idx]
				if value:
					parent_keys.append(value)
			writer.writerow(cleaned_row)

	return parent_idx, parent_keys


def write_parent_file_for_input(input_path: Path, parent_keys: List[str]) -> Tuple[Path, int]:
	# Keep order but deduplicate while preserving first occurrence
	seen = set()
	ordered_unique: List[str] = []
	for key in parent_keys:
		if key not in seen:
			seen.add(key)
			ordered_unique.append(key)
	count = len(ordered_unique)
	joined = ",".join(ordered_unique)
	# Enclose in parentheses and append a count line
	parent_text = f"({joined})\nparents found={count}\n"
	parent_file = input_path.with_name(f"{input_path.stem}-parents.txt")
	with open(parent_file, 'w', encoding='utf-8', newline='') as f:
		f.write(parent_text)
	return parent_file, count


def main() -> None:
	args = parse_args()
	input_path = Path(args.input)
	output_path = build_output_path(input_path, args.output)
	parent_idx, parent_keys = clean_csv(input_path, output_path)
	parent_file, parent_count = write_parent_file_for_input(input_path, parent_keys)
	if parent_idx is None:
		print("Warning: 'Parent key' column not found in header; parents file may be empty.")
	print(f"CSV file cleaned. Output saved to {output_path}")
	print(f"Found {parent_count} unique parents. Parent keys written to {parent_file}")


if __name__ == "__main__":
	main()
