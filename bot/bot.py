"""Telegram bot entry point with --test mode and aiogram transport."""

import argparse
import asyncio
import logging
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

try:
    from aiogram import Bot, Dispatcher, types
    from aiogram.filters import Command, CommandStart
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    AIGRAM_AVAILABLE = True
except ImportError:
    AIGRAM_AVAILABLE = False


# Inline keyboard buttons for common queries
INLINE_BUTTONS = [
    {"text": "📚 What labs?", "callback_data": "labs"},
    {"text": "💯 Lab 4 scores", "callback_data": "scores_lab-04"},
    {"text": "📊 Lowest pass rate", "callback_data": "lowest_pass_rate"},
    {"text": "🏆 Top students", "callback_data": "top_students"},
]


def get_inline_keyboard() -> InlineKeyboardMarkup:
    """Create inline keyboard with common queries."""
    keyboard = []
    row = []
    for i, btn in enumerate(INLINE_BUTTONS):
        row.append(InlineKeyboardButton(
            text=btn["text"],
            callback_data=btn["callback_data"],
        ))
        if (i + 1) % 2 == 0:  # 2 buttons per row
            keyboard.append(row)
            row = []
    if row:  # Add remaining buttons
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


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


async def telegram_mode_async(settings) -> None:
    """Run bot in Telegram mode using aiogram.
    
    Args:
        settings: Bot configuration settings.
    """
    if not AIGRAM_AVAILABLE:
        print("Error: aiogram not installed. Install with: pip install aiogram")
        sys.exit(1)
    
    if not settings.bot_token:
        print("Error: BOT_TOKEN not set. Check .env.bot.secret or environment.")
        sys.exit(1)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    logger = logging.getLogger(__name__)
    
    # Initialize bot and dispatcher
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    
    # Get inline keyboard
    keyboard = get_inline_keyboard()
    
    @dp.message(CommandStart())
    async def cmd_start(message: types.Message):
        """Handle /start command."""
        response = handle_start()
        await message.answer(response, reply_markup=keyboard)
    
    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        """Handle /help command."""
        response = handle_help()
        await message.answer(response)
    
    @dp.message(Command("health"))
    async def cmd_health(message: types.Message):
        """Handle /health command."""
        response = handle_health()
        await message.answer(response)
    
    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message):
        """Handle /labs command."""
        response = handle_labs()
        await message.answer(response)
    
    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message):
        """Handle /scores command."""
        lab_query = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
        response = handle_scores(lab_query)
        await message.answer(response)
    
    @dp.message(Command("botfather"))
    async def cmd_botfather(message: types.Message):
        """Handle /botfather command - setup instructions."""
        response = """To set up this bot with BotFather:

1. Open Telegram and search for @BotFather
2. Send /newbot
3. Choose a name (e.g., "My LMS Bot")
4. Choose a username ending in 'bot' (e.g., "my_lms_helper_bot")
5. Copy the token and set BOT_TOKEN in .env.bot.secret

Then restart the bot."""
        await message.answer(response)
    
    @dp.callback_query()
    async def handle_callback(callback: types.CallbackQuery):
        """Handle inline keyboard button clicks."""
        await callback.answer()  # Acknowledge the callback
        
        callback_map = {
            "labs": "/labs",
            "scores_lab-04": "/scores lab-04",
            "lowest_pass_rate": "which lab has the lowest pass rate",
            "top_students": "who are the top 5 students in lab 04",
        }
        
        query = callback_map.get(callback.data, "")
        if query:
            response = run_command(*parse_command(query))
            await callback.message.answer(response)
    
    @dp.message()
    async def handle_message(message: types.Message):
        """Handle all other messages (natural language)."""
        # Skip if message is a command (handled above)
        if message.text and message.text.startswith('/'):
            return
        
        # Use intent router for natural language
        response = handle_natural_language(message.text or "")
        await message.answer(response)
    
    # Start polling
    logger.info(f"Bot starting with token: {settings.bot_token[:10]}...")
    logger.info("Bot is ready! Send messages in Telegram.")
    
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot shutting down...")
    finally:
        await bot.close()


def telegram_mode(settings) -> None:
    """Run bot in Telegram mode.
    
    Args:
        settings: Bot configuration settings.
    """
    if not AIGRAM_AVAILABLE:
        print("Error: aiogram not installed. Install with: pip install aiogram")
        print("Inline buttons configured: 4")
        sys.exit(1)
    
    asyncio.run(telegram_mode_async(settings))


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
