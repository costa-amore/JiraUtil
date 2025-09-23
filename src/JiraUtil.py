from pathlib import Path

from jira_cleaner import run_remove_newlines
from csv_utils import run_extract_field_values
from jira_dates_eu import run as run_jira_dates_eu
from testfixture import run_TestFixture_Reset, run_assert_expectations, DEFAULT_TEST_FIXTURE_LABEL
from auth import get_jira_credentials
from cli import build_parser, show_list, show_status


def run_cli() -> dict:
    """Core CLI logic that can be tested independently.
    
    Returns:
        dict: Result information including command, success status, and any output
    """
    parser = build_parser()
    args = parser.parse_args()

    result = {
        'command': args.command,
        'subcommand': getattr(args, 'csv_command', None) or getattr(args, 'test_command', None),
        'success': True,
        'error': None
    }

    try:
        # Handle list command
        if args.command in ["list", "ls"]:
            show_list()
            return result
        
        # Handle status command
        if args.command in ["status", "st"]:
            show_status()
            return result

        # Handle csv-export commands (including aliases: ce)
        if args.command in ["csv-export", "ce"]:
            if args.csv_command in ["remove-newlines", "rn"]:
                input_path = Path(args.input)
                run_remove_newlines(input_path, args.output)
                return result
            if args.csv_command in ["extract-to-comma-separated-list", "ecl"]:
                input_path = Path(args.input)
                run_extract_field_values(input_path, args.field_name, None)
                return result
            if args.csv_command in ["fix-dates-eu", "fd"]:
                input_path = Path(args.input)
                run_jira_dates_eu(input_path, args.output)
                return result
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
                return result
            elif args.test_command in ["assert", "a"]:
                run_assert_expectations(jira_url, username, password, args.label)
                return result
            else:
                parser.error("Unknown test-fixture command")

        parser.error("Unknown command")
        
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
        raise


def main() -> None:
    """Main entry point for CLI."""
    run_cli()


if __name__ == "__main__":
    main()


