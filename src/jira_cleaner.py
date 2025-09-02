import csv
import re
from pathlib import Path
from typing import List, Tuple

# Characters that can cause Excel to interpret a new row when present inside fields
# Includes CR, LF, Unicode line/paragraph separators, and Next Line.
LINE_BREAK_PATTERN = re.compile(r"[\r\n\u2028\u2029\u0085]+")


def build_output_path(input_path: Path, explicit_output: str | None, suffix: str = "-cleaned") -> Path:
	if explicit_output:
		return Path(explicit_output)
	# Default: same folder, base name with suffix
	stem = input_path.stem
	# Always use .csv for output
	return input_path.with_name(f"{stem}{suffix}.csv")


def remove_newlines_from_csv(input_path: Path, output_path: Path) -> None:
	"""Remove newline characters from CSV fields to prevent Excel row breaks."""
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

		# Sanitize each field
		for row in reader:
			cleaned_row = []
			for field in row:
				# Replace any line-breaking characters with a single space
				cleaned_field = LINE_BREAK_PATTERN.sub(' ', field)
				# Optionally collapse repeated spaces created by replacements
				cleaned_field = re.sub(r'\s{2,}', ' ', cleaned_field).strip()
				cleaned_row.append(cleaned_field)
			writer.writerow(cleaned_row)


def run_remove_newlines(input_path: Path, output: str | None) -> None:
	"""Remove newline characters from CSV fields."""
	output_path = build_output_path(input_path, output, "-no-newlines")
	remove_newlines_from_csv(input_path, output_path)
	print(f"Newlines removed from CSV. Output saved to {output_path}")