import csv
from pathlib import Path
from typing import List
from dateutil import parser as dtparser


def _find_indices(header: List[str], targets: List[str]) -> List[int]:
	indices: List[int] = []
	normalized = [h.strip().lower() for h in header]
	for target in targets:
		try:
			idx = normalized.index(target.lower())
			indices.append(idx)
		except ValueError:
			indices.append(-1)
	return indices


def _format_eu(dt_str: str) -> str:
	# Try to parse; on failure, return original
	try:
		dt = dtparser.parse(dt_str)
		return dt.strftime('%d/%m/%Y %H:%M:%S')
	except Exception:
		return dt_str


def run(input_path: Path, output: str | None) -> None:
	# Determine output path
	if output:
		output_path = Path(output)
	else:
		output_path = input_path.with_name(f"{input_path.stem}-eu-dates.csv")

	with open(input_path, 'r', newline='', encoding='utf-8-sig') as infile, \
		open(output_path, 'w', newline='', encoding='utf-8') as outfile:
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

		header = next(reader, None)
		if header is None:
			print("Empty CSV; nothing to do.")
			return

		writer.writerow(header)
		created_idx, updated_idx = _find_indices(header, ["Created", "Updated"])

		for row in reader:
			# Ensure row length matches header for safety
			row = list(row)
			if 0 <= created_idx < len(row):
				row[created_idx] = _format_eu(row[created_idx])
			if 0 <= updated_idx < len(row):
				row[updated_idx] = _format_eu(row[updated_idx])
			writer.writerow(row)

	print(f"Dates converted for European Excel. Output saved to {output_path}")
