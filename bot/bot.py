"""Telegram bot entry point with --test mode and intent routing support."""

import argparse
import sys

from config import load_settings
from handlers import (
    handle_health,
    handle_help,
    handle_labs,
    handle_natural_language,
    handle_scores,
    handle_start,
)


# Inline keyboard buttons for common queries
INLINE_BUTTONS = [
    {"text": "📚 What labs?", "callback_data": "labs"},
    {"text": "💯 Lab 4 scores", "callback_data": "scores_lab-04"},
    {"text": "📊 Lowest pass rate", "callback_data": "lowest_pass_rate"},
    {"text": "🏆 Top students", "callback_data": "top_students"},
]


def parse_command(text: str) -> tuple[str, str]:
    """Parse command text into command and arguments.
    
    Args:
        text: User input text (e.g., "/scores lab-04" or "hello").
        
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
    # Slash commands
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
    
    # Natural language query - use intent router
    return handle_natural_language(f"{command} {args}".strip())


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
    # TODO: Implement Telegram bot client with aiogram (Task 4)
    # For now, show that intent routing is available
    print("Telegram mode: Intent routing ready (Task 4 will implement aiogram)")
    print(f"Inline buttons configured: {len(INLINE_BUTTONS)}")
    sys.exit(0)


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
