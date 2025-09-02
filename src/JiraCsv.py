import argparse
from pathlib import Path

from jira_cleaner import run_remove_newlines
from jira_field_extractor import run_extract_field_values
from jira_dates_eu import run as run_jira_dates_eu


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(prog="JiraCsv", description="Jira CSV utilities")
	subparsers = parser.add_subparsers(dest="command", required=True)

	# remove-newline subcommand
	remove_newline = subparsers.add_parser("remove-newline", help="Remove newline characters from CSV fields")
	remove_newline.add_argument("input", help="Path to the input Jira CSV file")
	remove_newline.add_argument("--output", "-o", help="Optional output CSV path; defaults to <input-stem>-no-newlines.csv next to input")

	# extract-to-comma-separated-list subcommand
	extract_field = subparsers.add_parser("extract-to-comma-separated-list", help="Extract field values from CSV and write to comma-separated text file")
	extract_field.add_argument("field_name", help="Name of the field to extract (e.g., 'Parent key', 'Assignee', 'Status')")
	extract_field.add_argument("input", help="Path to the input Jira CSV file")

	# fix-dates-eu subcommand
	fixdates = subparsers.add_parser("fix-dates-eu", help="Convert Created/Updated dates for European Excel")
	fixdates.add_argument("input", help="Path to the input Jira CSV file")
	fixdates.add_argument("--output", "-o", help="Optional output CSV path; defaults to <input-stem>-eu-dates.csv next to input")
	return parser


def main() -> None:
	parser = build_parser()
	args = parser.parse_args()

	if args.command == "remove-newline":
		input_path = Path(args.input)
		run_remove_newlines(input_path, args.output)
		return
	if args.command == "extract-to-comma-separated-list":
		input_path = Path(args.input)
		run_extract_field_values(input_path, args.field_name, None)
		return
	if args.command == "fix-dates-eu":
		input_path = Path(args.input)
		run_jira_dates_eu(input_path, args.output)
		return

	parser.error("Unknown command")


if __name__ == "__main__":
	main()


