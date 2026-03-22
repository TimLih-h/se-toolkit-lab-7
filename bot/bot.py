"""Telegram bot entry point with --test mode support."""

import argparse
import sys

from config import load_settings
from handlers import (
    handle_health,
    handle_help,
    handle_labs,
    handle_scores,
    handle_start,
)


def parse_command(text: str) -> tuple[str, str]:
    """Parse command text into command and arguments.
    
    Args:
        text: User input text (e.g., "/scores lab-04" or "/start").
        
    Returns:
        Tuple of (command, arguments).
    """
    parts = text.strip().split(maxsplit=1)
    command = parts[0].lower() if parts else ""
    args = parts[1] if len(parts) > 1 else ""
    return command, args


def run_command(command: str, args: str) -> str:
    """Execute a command and return the response.
    
    Args:
        command: Command name (e.g., "/start", "/help").
        args: Command arguments.
        
    Returns:
        Response text from the handler.
    """
    handlers = {
        "/start": lambda: handle_start(),
        "/help": lambda: handle_help(),
        "/health": lambda: handle_health(),
        "/labs": lambda: handle_labs(),
        "/scores": lambda: handle_scores(args),
    }
    
    handler = handlers.get(command)
    if handler:
        return handler()
    return f"Unknown command: {command}. Use /help to see available commands."


def test_mode(text: str) -> None:
    """Run bot in test mode (CLI).
    
    Args:
        text: Command text to execute.
    """
    command, args = parse_command(text)
    response = run_command(command, args)
    print(response)
    sys.exit(0)


def telegram_mode(settings) -> None:
    """Run bot in Telegram mode.
    
    Args:
        settings: Bot configuration settings.
    """
    # TODO: Implement Telegram bot client (Task 4)
    print("Telegram mode not implemented yet")
    sys.exit(1)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="TEXT",
        help="Run in test mode with the given command text",
    )
    args = parser.parse_args()
    
    # Load configuration
    settings = load_settings()
    
    if args.test:
        test_mode(args.test)
    else:
        telegram_mode(settings)


if __name__ == "__main__":
    main()
