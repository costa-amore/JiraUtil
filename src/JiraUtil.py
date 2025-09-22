import argparse
import json
import sys
from pathlib import Path

from jira_cleaner import run_remove_newlines
from jira_field_extractor import run_extract_field_values
from jira_dates_eu import run as run_jira_dates_eu
from jira_testfixture import run_TestFixture_Reset, run_assert_expectations, get_jira_credentials, DEFAULT_TEST_FIXTURE_LABEL


def get_version() -> str:
    """Get the current version from version.json."""
    try:
        version_file = Path("version.json")
        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                version_data = json.load(f)
                return f"{version_data['major']}.{version_data['minor']}.{version_data['build']}"
        else:
            return "unknown"
    except (json.JSONDecodeError, KeyError, IOError):
        return "unknown"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="JiraUtil", description="Jira utilities")
    
    # Add version argument
    parser.add_argument("-v", "--version", action="version", version=f"JiraUtil {get_version()}")
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    # csv-export subcommand group (alias: ce)
    csv_export = subparsers.add_parser("csv-export", aliases=["ce"], help="CSV export file processing commands")
    csv_subparsers = csv_export.add_subparsers(dest="csv_command", required=True)

    # remove-newlines subcommand under csv-export (alias: rn)
    remove_newline = csv_subparsers.add_parser("remove-newlines", aliases=["rn"], help="Remove newline characters from CSV fields")
    remove_newline.add_argument("input", help="Path to the input Jira CSV file")
    remove_newline.add_argument("--output", "-o", help="Optional output CSV path; defaults to <input-stem>-no-newlines.csv next to input")

    # extract-to-comma-separated-list subcommand under csv-export (alias: ecl) - KEEP AS IS
    extract_field = csv_subparsers.add_parser("extract-to-comma-separated-list", aliases=["ecl"], help="Extract field values from CSV and write to comma-separated text file")
    extract_field.add_argument("field_name", help="Name of the field to extract (e.g., 'Parent key', 'Assignee', 'Status')")
    extract_field.add_argument("input", help="Path to the input Jira CSV file")

    # fix-dates-eu subcommand under csv-export (alias: fd)
    fixdates = csv_subparsers.add_parser("fix-dates-eu", aliases=["fd"], help="Convert Created/Updated dates for European Excel")
    fixdates.add_argument("input", help="Path to the input Jira CSV file")
    fixdates.add_argument("--output", "-o", help="Optional output CSV path; defaults to <input-stem>-eu-dates.csv next to input")
    
    # test-fixture subcommand group (alias: tf)
    test_fixture = subparsers.add_parser("test-fixture", aliases=["tf"], help="Test fixture management commands")
    test_fixture_subparsers = test_fixture.add_subparsers(dest="test_command", required=True)
    
    # reset subcommand under test-fixture (alias: r)
    reset_test_fixture = test_fixture_subparsers.add_parser("reset", aliases=["r"], help="Process issues with specified label and update status based on summary pattern")
    reset_test_fixture.add_argument("label", nargs='?', default=DEFAULT_TEST_FIXTURE_LABEL, help=f"Jira label to search for (default: '{DEFAULT_TEST_FIXTURE_LABEL}')")
    reset_test_fixture.add_argument("--jira-url", help="Jira instance URL (can also be set via JIRA_URL environment variable)")
    reset_test_fixture.add_argument("--username", help="Jira username (can also be set via JIRA_USERNAME environment variable)")
    reset_test_fixture.add_argument("--password", help="Jira password/API token (can also be set via JIRA_PASSWORD environment variable)")
    
    # assert subcommand under test-fixture (alias: a)
    assert_expectations = test_fixture_subparsers.add_parser("assert", aliases=["a"], help="Assert that issues with specified label are in their expected status based on summary pattern")
    assert_expectations.add_argument("label", nargs='?', default=DEFAULT_TEST_FIXTURE_LABEL, help=f"Jira label to search for (default: '{DEFAULT_TEST_FIXTURE_LABEL}')")
    assert_expectations.add_argument("--jira-url", help="Jira instance URL (can also be set via JIRA_URL environment variable)")
    assert_expectations.add_argument("--username", help="Jira username (can also be set via JIRA_USERNAME environment variable)")
    assert_expectations.add_argument("--password", help="Jira password/API token (can also be set via JIRA_PASSWORD environment variable)")
    
    # list command
    list_cmd = subparsers.add_parser("list", aliases=["ls"], help="List available commands and their descriptions")
    
    # status command
    status_cmd = subparsers.add_parser("status", aliases=["st"], help="Show tool status and information")
    
    return parser


def show_list() -> None:
    """Show available commands and their descriptions."""
    print("JiraUtil - Available Commands")
    print("=" * 40)
    print()
    print("CSV Export Commands:")
    print("  csv-export remove-newlines <input>     Remove newline characters from CSV fields")
    print("  csv-export extract-to-comma-separated-list <field> <input>  Extract field values")
    print("  csv-export fix-dates-eu <input>        Convert dates for European Excel")
    print()
    print("Test Fixture Commands:")
    print("  test-fixture reset [label]             Reset test fixture issues")
    print("  test-fixture assert [label]            Assert test fixture expectations")
    print()
    print("Utility Commands:")
    print("  list                                   Show this command list")
    print("  status                                 Show tool status")
    print("  --version, -v                          Show version")
    print("  --help, -h                             Show help")
    print()
    print("Short Aliases:")
    print("  ce rn <input>                          csv-export remove-newlines")
    print("  ce ecl <field> <input>                 csv-export extract-to-comma-separated-list")
    print("  ce fd <input>                          csv-export fix-dates-eu")
    print("  tf r [label]                           test-fixture reset")
    print("  tf a [label]                           test-fixture assert")
    print("  ls                                     list")
    print("  st                                     status")


def show_status() -> None:
    """Show tool status and information."""
    print("JiraUtil Status")
    print("=" * 20)
    print(f"Version: {get_version()}")
    print("Status: Ready")
    print()
    print("Configuration:")
    print("  Jira credentials: Check .venv/jira_config.env or environment variables")
    print("  Default test fixture label: rule-testing")
    print()
    print("Available commands: Use 'JiraUtil list' or 'JiraUtil --help'")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Handle list command
    if args.command in ["list", "ls"]:
        show_list()
        return
    
    # Handle status command
    if args.command in ["status", "st"]:
        show_status()
        return

    # Handle csv-export commands (including aliases: ce)
    if args.command in ["csv-export", "ce"]:
        if args.csv_command in ["remove-newlines", "rn"]:
            input_path = Path(args.input)
            run_remove_newlines(input_path, args.output)
            return
        if args.csv_command in ["extract-to-comma-separated-list", "ecl"]:
            input_path = Path(args.input)
            run_extract_field_values(input_path, args.field_name, None)
            return
        if args.csv_command in ["fix-dates-eu", "fd"]:
            input_path = Path(args.input)
            run_jira_dates_eu(input_path, args.output)
            return
        parser.error("Unknown csv-export command")
    
    # Handle test-fixture commands (including aliases: tf)
    if args.command in ["test-fixture", "tf"]:
        # Get Jira credentials from arguments or environment
        jira_url = args.jira_url
        username = args.username
        password = args.password
        
        # If not provided via arguments, get from environment or prompt
        if not jira_url or not username or not password:
            env_url, env_username, env_password = get_jira_credentials()
            jira_url = jira_url or env_url
            username = username or env_username
            password = password or env_password
        
        if args.test_command in ["reset", "r"]:
            run_TestFixture_Reset(jira_url, username, password, args.label)
            return
        elif args.test_command in ["assert", "a"]:
            run_assert_expectations(jira_url, username, password, args.label)
            return
        else:
            parser.error("Unknown test-fixture command")

    parser.error("Unknown command")


if __name__ == "__main__":
    main()


