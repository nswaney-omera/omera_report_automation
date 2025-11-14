"""
REST API logging module for MCP tool usage tracking.

This module handles logging all MCP tool invocations to a remote webservice.
Uses HTTP POST requests to send log data to a configured endpoint.

Environment Variables:
    MCP_LOG_URL: The webservice endpoint URL (required)
    MCP_LOG_AUTH_TOKEN: Optional authorization token for the API
"""

import json
import os
import sys
import requests
import socket
import getpass
from datetime import datetime
from typing import Any, Dict, Optional
import traceback


class DatabaseLogger:
    """Handles REST API connection and logging operations."""

    def __init__(self):
        """Initialize logger with API endpoint from environment variables."""
        self.base_url = os.environ.get(
            'MCP_LOG_URL',
            'http://ai.omerapartners.com/api/AIReportGeneratorLog/LogAIGeneratedExecutiveReport'
        )
        self.headers = {
            'Content-Type': 'application/json'
        }
        
        # Add authorization token if provided
        auth_token = os.environ.get('MCP_LOG_AUTH_TOKEN')
        if auth_token:
            self.headers['Authorization'] = f'Bearer {auth_token}'
        
        self.initialized = True
        self._error_count = 0
        self._max_errors = 5  # Stop trying after 5 consecutive errors

    def get_system_user_info(self) -> Dict[str, str]:
        """
        Gather system and user information.
        
        Returns:
            Dictionary with system information
        """
        try:
            return {
                "username": getpass.getuser(),
                "hostname": socket.gethostname()
            }
        except Exception as e:
            print(f"Error gathering system info: {str(e)}", file=sys.stderr)
            return {
                "username": "unknown",
                "hostname": "unknown"
            }

    def initialize_schema(self):
        """
        No schema initialization needed for REST API.
        This method is kept for compatibility with the original interface.
        """
        pass

    def log_tool_usage(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        user_info: Optional[Dict[str, Any]],
        success: bool,
        execution_time_ms: int,
        output_preview: str = "",
        error_message: str = ""
    ) -> tuple[bool, str]:
        """Log a tool usage event to the REST API."""
        
        if self._error_count >= self._max_errors:
            return False, f"API logging disabled after {self._max_errors} consecutive errors"

        try:
            # Get timestamp
            timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

            # Serialize parameters with truncation
            try:
                parameters_json = json.dumps(parameters, default=str)
                original_params_len = len(parameters_json)
                # TRUNCATE to fit database column (assume max 255 or 500 chars)
                if len(parameters_json) > 255:
                    parameters_json = parameters_json[:252] + "..."
                    print(f"Warning: Parameters truncated from {original_params_len} to 255 chars", file=sys.stderr)
            except Exception as e:
                print(f"Failed to serialize parameters: {e}", file=sys.stderr)
                parameters_json = json.dumps({"error": "serialization_failed"})
            
            # Get and serialize user_info with truncation
            if user_info:
                combined_user_info = {**self.get_system_user_info(), **user_info}
            else:
                combined_user_info = self.get_system_user_info()
            
            try:
                user_info_json = json.dumps(combined_user_info, default=str)
                original_user_info_len = len(user_info_json)
                # TRUNCATE to fit database column
                if len(user_info_json) > 255:
                    user_info_json = user_info_json[:252] + "..."
                    print(f"Warning: User info truncated from {original_user_info_len} to 255 chars", file=sys.stderr)
            except Exception as e:
                print(f"Failed to serialize user_info: {e}", file=sys.stderr)
                user_info_json = json.dumps({"username": "unknown", "hostname": "unknown"})

            # Truncate tool_name if needed
            tool_name_truncated = tool_name[:100] if len(tool_name) > 100 else tool_name

            # Truncate output_preview if needed (limit to 500 chars)
            output_preview_truncated = ""
            if output_preview:
                output_preview_truncated = output_preview[:500] if len(output_preview) > 500 else output_preview
                if len(output_preview) > 500:
                    print(f"Warning: Output preview truncated from {len(output_preview)} to 500 chars", file=sys.stderr)
            
            # Truncate error_message if needed (limit to 500 chars)
            error_message_truncated = ""
            if error_message:
                error_message_truncated = error_message[:500] if len(error_message) > 500 else error_message
                if len(error_message) > 500:
                    print(f"Warning: Error message truncated from {len(error_message)} to 500 chars", file=sys.stderr)

            # Build payload
            payload = {
                "timestamp": timestamp,
                "tool_name": tool_name_truncated,
                "parameters": parameters_json,
                "user_info": user_info_json,
                "success": 1 if success else 0,
                "execution_time_ms": int(execution_time_ms),
                "output_preview": output_preview_truncated,
                "error_message": error_message_truncated
            }

            # DEBUG OUTPUT - See exactly what's being sent
            print("\n" + "="*70, file=sys.stderr)
            print(f"LOGGING PAYLOAD FOR: {tool_name}", file=sys.stderr)
            print("="*70, file=sys.stderr)
            print(f"tool_name length: {len(tool_name_truncated)} chars", file=sys.stderr)
            print(f"parameters length: {len(parameters_json)} chars", file=sys.stderr)
            print(f"user_info length: {len(user_info_json)} chars", file=sys.stderr)
            print(f"timestamp length: {len(timestamp)} chars", file=sys.stderr)
            print(f"output_preview length: {len(output_preview_truncated)} chars", file=sys.stderr)
            print(f"error_message length: {len(error_message_truncated)} chars", file=sys.stderr)
            print(f"\nFull payload:", file=sys.stderr)
            print(json.dumps(payload, indent=2), file=sys.stderr)
            print("="*70 + "\n", file=sys.stderr)

            # Send request
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            # DEBUG OUTPUT - See response
            print(f"API Response Status: {response.status_code}", file=sys.stderr)
            if response.status_code == 200:
                print(f"API Response Body: {response.text[:200]}", file=sys.stderr)
            else:
                print(f"API Error Response: {response.text[:1000]}", file=sys.stderr)
            
            response.raise_for_status()
            self._error_count = 0
            return True, ""

        except requests.exceptions.RequestException as e:
            self._error_count += 1
            error_msg = f"API request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nStatus: {e.response.status_code}\nBody: {e.response.text[:500]}"
            print(error_msg, file=sys.stderr)
            return False, error_msg

        except Exception as e:
            self._error_count += 1
            error_msg = f"Unexpected error: {str(e)}"
            print(f"{error_msg}\n{traceback.format_exc()}", file=sys.stderr)
            return False, error_msg


# Global logger instance
_logger = DatabaseLogger()


def log_tool_usage(
    tool_name: str,
    parameters: Dict[str, Any],
    user_info: Optional[Dict[str, Any]],
    success: bool,
    execution_time_ms: int,
    output_preview: str = "",
    error_message: str = ""
) -> tuple[bool, str]:
    """
    Convenience function to log tool usage via the global logger instance.

    See DatabaseLogger.log_tool_usage() for parameter documentation.

    Returns:
        Tuple of (success: bool, message: str)
    """
    return _logger.log_tool_usage(
        tool_name=tool_name,
        parameters=parameters,
        user_info=user_info,
        success=success,
        execution_time_ms=execution_time_ms,
        output_preview=output_preview,
        error_message=error_message
    )


# For backward compatibility - no database path in REST API version
def get_database_path():
    """
    Returns None - no local database in REST API version.
    This function is kept for backward compatibility.
    """
    return None


# Test the logger when running directly
if __name__ == "__main__":
    print("Testing MCP REST API Logger...")
    
    # Test with sample data
    sample_parameters = {
        "report_id": "exec_summary_001",
        "query": "Generate executive summary"
    }
    
    success, message = log_tool_usage(
        tool_name="test_tool",
        parameters=sample_parameters,
        user_info={"client": "test_client"},
        success=True,
        execution_time_ms=150,
        output_preview="Sample output preview text..."
    )
    
    if success:
        print("✓ Logging succeeded")
    else:
        print(f"✗ Logging failed: {message}")