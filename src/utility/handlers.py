from cli import show_list, show_status


def handle_list_command(args, result: dict) -> dict:
    """Handle list command."""
    show_list()
    return result


def handle_status_command(args, result: dict) -> dict:
    """Handle status command."""
    show_status()
    return result
