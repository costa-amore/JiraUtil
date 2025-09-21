import argparse
from pathlib import Path

from jira_cleaner import run_remove_newlines
from jira_field_extractor import run_extract_field_values
from jira_dates_eu import run as run_jira_dates_eu
from jira_reset_testfixture import run_TestFixture_Reset, run_assert_expectations, get_jira_credentials


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="JiraUtil", description="Jira utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # CsvExport subcommand group (alias: ce)
    csv_export = subparsers.add_parser("CsvExport", aliases=["ce"], help="CSV export file processing commands")
    csv_subparsers = csv_export.add_subparsers(dest="csv_command", required=True)

    # remove-newline subcommand under CsvExport (alias: rn)
    remove_newline = csv_subparsers.add_parser("remove-newline", aliases=["rn"], help="Remove newline characters from CSV fields")
    remove_newline.add_argument("input", help="Path to the input Jira CSV file")
    remove_newline.add_argument("--output", "-o", help="Optional output CSV path; defaults to <input-stem>-no-newlines.csv next to input")

    # extract-to-comma-separated-list subcommand under CsvExport (alias: ecl)
    extract_field = csv_subparsers.add_parser("extract-to-comma-separated-list", aliases=["ecl"], help="Extract field values from CSV and write to comma-separated text file")
    extract_field.add_argument("field_name", help="Name of the field to extract (e.g., 'Parent key', 'Assignee', 'Status')")
    extract_field.add_argument("input", help="Path to the input Jira CSV file")

    # fix-dates-eu subcommand under CsvExport (alias: fd)
    fixdates = csv_subparsers.add_parser("fix-dates-eu", aliases=["fd"], help="Convert Created/Updated dates for European Excel")
    fixdates.add_argument("input", help="Path to the input Jira CSV file")
    fixdates.add_argument("--output", "-o", help="Optional output CSV path; defaults to <input-stem>-eu-dates.csv next to input")
    
    # ResetTestFixture subcommand (alias: rt)
    reset_test_fixture = subparsers.add_parser("ResetTestFixture", aliases=["rt"], help="Process issues with specified label and update status based on summary pattern")
    reset_test_fixture.add_argument("label", nargs='?', default="rule-testing", help="Jira label to search for (default: 'rule-testing')")
    reset_test_fixture.add_argument("--jira-url", help="Jira instance URL (can also be set via JIRA_URL environment variable)")
    reset_test_fixture.add_argument("--username", help="Jira username (can also be set via JIRA_USERNAME environment variable)")
    reset_test_fixture.add_argument("--password", help="Jira password/API token (can also be set via JIRA_PASSWORD environment variable)")
    
    # AssertExpectations subcommand (alias: ae)
    assert_expectations = subparsers.add_parser("AssertExpectations", aliases=["ae"], help="Assert that issues with specified label are in their expected status based on summary pattern")
    assert_expectations.add_argument("label", nargs='?', default="rule-testing", help="Jira label to search for (default: 'rule-testing')")
    assert_expectations.add_argument("--jira-url", help="Jira instance URL (can also be set via JIRA_URL environment variable)")
    assert_expectations.add_argument("--username", help="Jira username (can also be set via JIRA_USERNAME environment variable)")
    assert_expectations.add_argument("--password", help="Jira password/API token (can also be set via JIRA_PASSWORD environment variable)")
    
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Handle CsvExport commands (including aliases: ce)
    if args.command in ["CsvExport", "ce"]:
        if args.csv_command in ["remove-newline", "rn"]:
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
        parser.error("Unknown CsvExport command")
    
    # Handle ResetTestFixture commands (including alias: rt)
    if args.command in ["ResetTestFixture", "rt"]:
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
        
        run_TestFixture_Reset(jira_url, username, password, args.label)
        return
    
    # Handle AssertExpectations commands (including alias: ae)
    if args.command in ["AssertExpectations", "ae"]:
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
        
        run_assert_expectations(jira_url, username, password, args.label)
        return

    parser.error("Unknown command")


if __name__ == "__main__":
    main()


