"""Intent router using LLM for natural language understanding."""

import json
import sys
from typing import Any, Optional

from config import load_settings
from services import create_lms_client, create_llm_client


# System prompt for the LLM to encourage tool use
SYSTEM_PROMPT = """You are an AI assistant for a Learning Management System (LMS). 
Your job is to help users understand their lab progress, scores, and performance.

You have access to tools that fetch real data from the LMS backend. 
When a user asks a question, you should:
1. Think about what data you need to answer
2. Call the appropriate tool(s) to get that data
3. Analyze the results
4. Provide a clear, helpful answer based on the actual data

If the user's message is a greeting (like "hello", "hi"), respond warmly and mention what you can help with.
If the message is unclear or seems like gibberish, politely ask for clarification and suggest what you can do.
If the user mentions a lab without a clear question, ask what they want to know about it.

Always use tools to get real data before making claims about scores, pass rates, or rankings.
"""


class IntentRouter:
    """Routes user messages to appropriate tools using LLM."""

    def __init__(self):
        """Initialize the intent router."""
        settings = load_settings()
        self.lms_client = create_lms_client(
            settings.lms_api_base_url,
            settings.lms_api_key,
        )
        self.llm_client = create_llm_client(
            settings.llm_api_base_url,
            settings.llm_api_key,
            settings.llm_api_model,
        )
        self.tools = self.llm_client.get_tool_definitions()

    def _execute_tool(self, name: str, arguments: dict) -> Any:
        """Execute a tool and return the result.
        
        Args:
            name: Tool/function name.
            arguments: Tool arguments as a dict.
            
        Returns:
            Tool result (usually a list or dict).
        """
        print(f"[tool] LLM called: {name}({json.dumps(arguments)})", file=sys.stderr)
        
        try:
            if name == "get_items":
                result = self.lms_client.get_items()
            elif name == "get_learners":
                result = self.lms_client.get_learners()
            elif name == "get_scores":
                result = self.lms_client.get_scores(arguments.get("lab", ""))
            elif name == "get_pass_rates":
                result = self.lms_client.get_pass_rates(arguments.get("lab", ""))
            elif name == "get_timeline":
                result = self.lms_client.get_timeline(arguments.get("lab", ""))
            elif name == "get_groups":
                result = self.lms_client.get_groups(arguments.get("lab", ""))
            elif name == "get_top_learners":
                lab = arguments.get("lab", "")
                limit = arguments.get("limit", 5)
                result = self.lms_client.get_top_learners(lab, limit)
            elif name == "get_completion_rate":
                result = self.lms_client.get_completion_rate(arguments.get("lab", ""))
            elif name == "trigger_sync":
                result = self.lms_client.trigger_sync()
            else:
                result = {"error": f"Unknown tool: {name}"}
            
            print(f"[tool] Result: {len(result) if isinstance(result, (list, dict)) else 'N/A'} items", file=sys.stderr)
            return result
        except Exception as e:
            print(f"[tool] Error: {str(e)}", file=sys.stderr)
            return {"error": str(e)}

    def route(self, message: str) -> str:
        """Route a user message to appropriate tools and return response.
        
        Args:
            message: User's natural language message.
            
        Returns:
            Formatted response text.
        """
        # Initialize conversation with system prompt
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]
        
        max_iterations = 5  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call LLM with current conversation state
            try:
                response = self.llm_client.chat_with_tools(messages, self.tools)
            except Exception as e:
                return f"LLM error: {str(e)}. The AI service may be temporarily unavailable."
            
            # Get the assistant's message
            assistant_message = response.get("choices", [{}])[0].get("message", {})
            
            # Check if LLM wants to call any tools
            tool_calls = assistant_message.get("tool_calls", [])
            
            if not tool_calls:
                # No tool calls - LLM has a final answer
                content = assistant_message.get("content", "I don't have enough information to answer that.")
                return content or "I don't have enough information to answer that."
            
            # Add assistant message to conversation
            messages.append(assistant_message)
            
            # Execute each tool call
            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                name = function.get("name", "")
                arguments_str = function.get("arguments", "{}")
                
                try:
                    arguments = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
                except json.JSONDecodeError:
                    arguments = {}
                
                # Execute the tool
                result = self._execute_tool(name, arguments)
                
                # Add tool result to conversation
                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", "unknown"),
                    "content": json.dumps(result, default=str),
                }
                messages.append(tool_message)
            
            print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)
        
        # If we get here, we hit max iterations
        return "I'm having trouble processing this request. Let me try to help with what I know: I can show you labs, scores, pass rates, and more. What would you like to know?"


def create_intent_router() -> IntentRouter:
    """Create an intent router instance."""
    return IntentRouter()
