import argparse
from pathlib import Path

from jira_cleaner import run as run_jira_cleaner


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(prog="py-runner", description="Utilities runner")
	subparsers = parser.add_subparsers(dest="command", required=True)

	# clean-jira subcommand
	clean = subparsers.add_parser("clean-jira", help="Clean Jira CSV and extract parents")
	clean.add_argument("input", help="Path to the input Jira CSV file")
	clean.add_argument("--output", "-o", help="Optional output CSV path; defaults to <input-stem>-cleaned.csv next to input")
	return parser


def main() -> None:
	parser = build_parser()
	args = parser.parse_args()

	if args.command == "clean-jira":
		input_path = Path(args.input)
		run_jira_cleaner(input_path, args.output)
		return

	parser.error("Unknown command")


if __name__ == "__main__":
	main()
