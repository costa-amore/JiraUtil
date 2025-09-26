"""
Command-line argument parser for Jira utilities.
"""

import argparse
from version import get_version
from testfixture import DEFAULT_TEST_FIXTURE_LABEL


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
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
    
    # trigger subcommand under test-fixture (alias: t)
    trigger_operation = test_fixture_subparsers.add_parser("trigger", aliases=["t"], help="Trigger automation rules by setting labels on a specific issue")
    trigger_operation.add_argument("-l", "--label", required=True, help="Label(s) to trigger automation rules (comma-separated for multiple labels)")
    trigger_operation.add_argument("-k", "--key", default="TAPS-212", help="Issue key to trigger (default: TAPS-212)")
    trigger_operation.add_argument("--jira-url", help="Jira instance URL (can also be set via JIRA_URL environment variable)")
    trigger_operation.add_argument("--username", help="Jira username (can also be set via JIRA_USERNAME environment variable)")
    trigger_operation.add_argument("--password", help="Jira password/API token (can also be set via JIRA_PASSWORD environment variable)")
    
    # list command
    list_cmd = subparsers.add_parser("list", aliases=["ls"], help="List available commands and their descriptions")
    
    # status command
    status_cmd = subparsers.add_parser("status", aliases=["st"], help="Show tool status and information")
    
    return parser
