"""
MCP tool logging decorator.

This module provides a decorator to automatically log all MCP tool calls
to the remote API for usage tracking and analytics.

Key Features:
- Automatically logs tool name, parameters, execution time, and success status
- Handles both synchronous and asynchronous tools
- Non-blocking: If logging fails, the tool execution continues normally
- Error resilience: After 5 consecutive failures, stops attempting to log
"""

import functools
import inspect
import time
from typing import Any, Callable, Dict, Optional
import sys

from .logging_db import log_tool_usage


def extract_user_info() -> Optional[Dict[str, Any]]:
    """
    Extract user/client information from the execution context.

    This attempts to capture information about who is calling the MCP tool.
    Currently returns basic environment info, but can be extended to capture
    MCP client information when available.

    Returns:
        Dictionary with user/client context, or None if not available
    """
    import os
    import platform

    user_info = {
        "username": os.environ.get("USER") or os.environ.get("USERNAME"),
        "hostname": platform.node()
        # Additional MCP-specific context can be added here when available
        # For example, if FastMCP provides request context with client info
    }

    return user_info


def log_mcp_tool(func: Callable) -> Callable:
    """
    Decorator to log MCP tool invocations to the remote API.

    This decorator wraps MCP tool functions and automatically logs:
    - Tool name
    - Input parameters (all arguments)
    - User/client context
    - Execution time in milliseconds
    - Success/failure status
    - Error messages (if tool fails)

    If logging fails, a warning is added to the tool's return value
    but the tool execution continues normally.

    Usage:
        @mcp.tool()
        @log_mcp_tool
        def my_tool(param1: str, param2: int) -> str:
            return "result"

    Args:
        func: The MCP tool function to wrap

    Returns:
        Wrapped function with logging
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Capture start time
        start_time = time.time()

        # Get tool name
        tool_name = func.__name__

        # Build parameters dictionary from args and kwargs
        # Get function signature to map args to parameter names
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())

        parameters = {}

        # Map positional args to parameter names
        for i, arg in enumerate(args):
            if i < len(param_names):
                parameters[param_names[i]] = arg

        # Add keyword arguments
        parameters.update(kwargs)

        # Extract user/client information
        user_info = extract_user_info()

        # Execute the tool
        success = False
        error_message = ""
        output = None

        try:
            output = func(*args, **kwargs)
            success = True
        except Exception as e:
            error_message = f"{type(e).__name__}: {str(e)}"
            # Re-raise the exception to maintain normal error handling
            raise
        finally:
            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)

            # Create output preview (for future use, not sent to API currently)
            output_preview = ""
            if output is not None:
                output_str = str(output)
                # Truncate at 500 characters
                output_preview = output_str[:500]
                if len(output_str) > 500:
                    output_preview += "..."

            # Log to API
            log_success, log_error = log_tool_usage(
                tool_name=tool_name,
                parameters=parameters,
                user_info=user_info,
                success=success,
                execution_time_ms=execution_time_ms,
                output_preview=output_preview,
                error_message=error_message
            )

            # If logging failed and tool succeeded, add warning to output
            if not log_success and success:
                warning_message = f"\n\n⚠️  Warning: Failed to log tool usage: {log_error}"

                # Try to append warning to output if it's a string
                if isinstance(output, str):
                    output = output + warning_message
                else:
                    # If not a string, print warning to stderr
                    print(warning_message, file=sys.stderr)

        return output

    return wrapper


def log_mcp_tool_async(func: Callable) -> Callable:
    """
    Async version of log_mcp_tool decorator for async MCP tools.

    Usage:
        @mcp.tool()
        @log_mcp_tool_async
        async def my_async_tool(param1: str) -> str:
            return "result"

    Args:
        func: The async MCP tool function to wrap

    Returns:
        Wrapped async function with logging
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        # Capture start time
        start_time = time.time()

        # Get tool name
        tool_name = func.__name__

        # Build parameters dictionary
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())

        parameters = {}
        for i, arg in enumerate(args):
            if i < len(param_names):
                parameters[param_names[i]] = arg
        parameters.update(kwargs)

        # Extract user/client information
        user_info = extract_user_info()

        # Execute the tool
        success = False
        error_message = ""
        output = None

        try:
            output = await func(*args, **kwargs)
            success = True
        except Exception as e:
            error_message = f"{type(e).__name__}: {str(e)}"
            raise
        finally:
            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)

            # Create output preview
            output_preview = ""
            if output is not None:
                output_str = str(output)
                output_preview = output_str[:500]
                if len(output_str) > 500:
                    output_preview += "..."

            # Log to API (this is sync, but should be fast enough)
            log_success, log_error = log_tool_usage(
                tool_name=tool_name,
                parameters=parameters,
                user_info=user_info,
                success=success,
                execution_time_ms=execution_time_ms,
                output_preview=output_preview,
                error_message=error_message
            )

            # Add warning if logging failed
            if not log_success and success:
                warning_message = f"\n\n⚠️  Warning: Failed to log tool usage: {log_error}"

                if isinstance(output, str):
                    output = output + warning_message
                else:
                    print(warning_message, file=sys.stderr)

        return output

    return wrapper