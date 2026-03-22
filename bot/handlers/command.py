"""Command handlers implementation."""


def handle_start() -> str:
    """Handle /start command.
    
    Returns:
        Welcome message for new users.
    """
    return "Welcome to the LMS Bot! Use /help to see available commands."


def handle_help() -> str:
    """Handle /help command.
    
    Returns:
        List of available commands with descriptions.
    """
    return """Available commands:
/start - Welcome message and bot introduction
/help - Show this help message
/health - Check backend API health status
/labs - List available labs
/scores <lab> - Get your scores for a specific lab"""


def handle_health() -> str:
    """Handle /health command.
    
    Returns:
        Backend API health status (placeholder).
    """
    return "Health check: Not implemented yet (Task 2)"


def handle_labs() -> str:
    """Handle /labs command.
    
    Returns:
        List of available labs (placeholder).
    """
    return "Available labs: Not implemented yet (Task 2)"


def handle_scores(lab_query: str = "") -> str:
    """Handle /scores command.
    
    Args:
        lab_query: Lab identifier or name from user input.
        
    Returns:
        User's scores for the specified lab (placeholder).
    """
    if not lab_query:
        return "Please specify a lab, e.g., /scores lab-04"
    return f"Scores for {lab_query}: Not implemented yet (Task 2)"
