from pathlib import Path

from jira_cleaner import run_remove_newlines
from csv_utils import run_extract_field_values
from jira_dates_eu import run as run_jira_dates_eu


# =============================================================================
# PUBLIC METHODS (sorted alphabetically)
# =============================================================================

def handle_csv_export_commands(args, result: dict) -> dict:
    """Handle csv-export commands."""
    csv_handlers = {
        "remove-newlines": remove_newlines,
        "rn": remove_newlines,
        "extract-to-comma-separated-list": extract_field_values,
        "ecl": extract_field_values,
        "fix-dates-eu": fix_dates_eu,
        "fd": fix_dates_eu,
    }
    
    handler = csv_handlers.get(args.csv_command)
    if handler:
        return handler(args, result)
    
    from cli.parser import build_parser
    parser = build_parser()
    parser.error("Unknown csv-export command")


# =============================================================================
# PRIVATE METHODS (sorted alphabetically)
# =============================================================================

def extract_field_values(args, result: dict) -> dict:
    input_path = Path(args.input)
    run_extract_field_values(input_path, args.field_name, None)
    return result


def fix_dates_eu(args, result: dict) -> dict:
    input_path = Path(args.input)
    run_jira_dates_eu(input_path, args.output)
    return result


def remove_newlines(args, result: dict) -> dict:
    input_path = Path(args.input)
    run_remove_newlines(input_path, args.output)
    return result