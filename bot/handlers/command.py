"""Command handlers implementation."""

import httpx
from typing import Optional

from config import load_settings
from services import create_lms_client
from .intent_router import create_intent_router


def _get_lms_client():
    """Create LMS client from settings."""
    settings = load_settings()
    return create_lms_client(settings.lms_api_base_url, settings.lms_api_key)


def handle_start() -> str:
    """Handle /start command.
    
    Returns:
        Welcome message for new users.
    """
    return """Welcome to the LMS Bot! 

I can help you explore lab data, scores, and performance analytics.

Try asking me:
• "What labs are available?"
• "Show me scores for lab 4"
• "Which lab has the lowest pass rate?"
• "Who are the top 5 students in lab 04?"

Or use /help to see all commands."""


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
/scores <lab> - Get pass rates for a specific lab

You can also ask me questions in plain English:
• "What labs are available?"
• "Show me scores for lab 4"
• "Which lab has the lowest pass rate?"
• "Who are the top students?"
• "Compare groups in lab 3\""""


def handle_health() -> str:
    """Handle /health command.
    
    Returns:
        Backend API health status with item count or error message.
    """
    try:
        client = _get_lms_client()
        items = client.get_items()
        return f"Backend is healthy. {len(items)} items available."
    except httpx.ConnectError as e:
        return f"Backend error: connection refused. Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except httpx.HTTPError as e:
        return f"Backend error: {str(e)}"
    except Exception as e:
        return f"Backend error: {str(e)}"


def handle_labs() -> str:
    """Handle /labs command.
    
    Returns:
        Formatted list of available labs or error message.
    """
    try:
        client = _get_lms_client()
        items = client.get_items()
        
        # Filter only labs (type == "lab")
        labs = [item for item in items if item.get("type") == "lab"]
        
        if not labs:
            return "No labs available."
        
        lines = ["Available labs:"]
        for lab in labs:
            title = lab.get("title", "Unknown")
            lines.append(f"- {title}")
        
        return "\n".join(lines)
    except httpx.ConnectError as e:
        return f"Backend error: connection refused. Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except httpx.HTTPError as e:
        return f"Backend error: {str(e)}"
    except Exception as e:
        return f"Backend error: {str(e)}"


def handle_scores(lab_query: str = "") -> str:
    """Handle /scores command.
    
    Args:
        lab_query: Lab identifier or name from user input.
        
    Returns:
        Formatted pass rates for the specified lab or error message.
    """
    if not lab_query:
        return "Please specify a lab, e.g., /scores lab-04"
    
    try:
        client = _get_lms_client()
        pass_rates = client.get_pass_rates(lab_query)
        
        if not pass_rates:
            return f"No pass rate data available for {lab_query}."
        
        lines = [f"Pass rates for {lab_query}:"]
        for rate in pass_rates:
            task_name = rate.get("task", rate.get("task_name", rate.get("task_title", "Unknown task")))
            pass_rate = rate.get("avg_score", rate.get("pass_rate", 0))
            if pass_rate < 1:
                pass_rate = pass_rate * 100
            attempts = rate.get("attempts", 0)
            lines.append(f"- {task_name}: {pass_rate:.1f}% ({attempts} attempts)")
        
        return "\n".join(lines)
    except httpx.ConnectError as e:
        return f"Backend error: connection refused. Check that the services are running."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Lab '{lab_query}' not found. Use /labs to see available labs."
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except httpx.HTTPError as e:
        return f"Backend error: {str(e)}"
    except Exception as e:
        return f"Backend error: {str(e)}"


def handle_natural_language(message: str) -> str:
    """Handle natural language queries using LLM intent routing.
    
    Args:
        message: User's natural language message.
        
    Returns:
        Response from the intent router.
    """
    try:
        router = create_intent_router()
        return router.route(message)
    except Exception as e:
        return f"Intent routing error: {str(e)}"
