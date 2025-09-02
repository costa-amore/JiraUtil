import argparse
from pathlib import Path

from jira_cleaner import run_remove_newlines
from jira_parent_extractor import run_extract_parent_keys
from jira_dates_eu import run as run_jira_dates_eu


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(prog="JiraCsv", description="Jira CSV utilities")
	subparsers = parser.add_subparsers(dest="command", required=True)

	# remove-newline subcommand
	remove_newline = subparsers.add_parser("remove-newline", help="Remove newline characters from CSV fields")
	remove_newline.add_argument("input", help="Path to the input Jira CSV file")
	remove_newline.add_argument("--output", "-o", help="Optional output CSV path; defaults to <input-stem>-no-newlines.csv next to input")

	# extract-parent-key subcommand
	extract_parent = subparsers.add_parser("extract-parent-key", help="Extract parent keys from CSV and write to text file")
	extract_parent.add_argument("input", help="Path to the input Jira CSV file")

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
	if args.command == "extract-parent-key":
		input_path = Path(args.input)
		run_extract_parent_keys(input_path, None)
		return
	if args.command == "fix-dates-eu":
		input_path = Path(args.input)
		run_jira_dates_eu(input_path, args.output)
		return

	parser.error("Unknown command")


if __name__ == "__main__":
	main()


