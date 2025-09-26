from cli import build_parser
from csv_export import handle_csv_export_commands
from test_fixture import handle_test_fixture_commands
from utility import handle_list_command, handle_status_command


# Public Methods
def main() -> None:
    """Main entry point for CLI."""
    run_cli()


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
        command_handlers = {
            "list": handle_list_command,
            "ls": handle_list_command,
            "status": handle_status_command,
            "st": handle_status_command,
            "csv-export": handle_csv_export_commands,
            "ce": handle_csv_export_commands,
            "test-fixture": handle_test_fixture_commands,
            "tf": handle_test_fixture_commands,
        }
        
        handler = command_handlers.get(args.command)
        if handler:
            return handler(args, result)
        
        parser.error("Unknown command")
        
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
        raise


if __name__ == "__main__":
    main()