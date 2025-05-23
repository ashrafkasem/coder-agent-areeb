"""
System tools for command execution and system information.
"""

import os
import platform
import subprocess
from typing import Dict, Any, Optional


class CommandRunner:
    """Tool for running shell commands."""
    
    @staticmethod
    def get_definition() -> Dict[str, Any]:
        """Get tool definition."""
        return {
            "name": "run_command",
            "description": "Run a shell command and get its output.",
            "parameters": {
                "command": {
                    "type": "string",
                    "description": "The command to run."
                },
                "timeout": {
                    "type": "integer",
                    "description": "Optional timeout in seconds (default: 30)."
                }
            },
            "output": "The command output (stdout and stderr) and return code."
        }
    
    @staticmethod
    def execute(params: Dict[str, Any]) -> str:
        """
        Run a shell command.
        
        Args:
            params: Dictionary with command and optional timeout
            
        Returns:
            Command output
        """
        command = params.get("command")
        timeout = params.get("timeout", 30)
        
        if not command:
            return "Error: command is required"
        
        try:
            # Run the command with timeout
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            stdout = process.stdout
            stderr = process.stderr
            returncode = process.returncode
            
            result = f"Command: {command}\n"
            result += f"Exit code: {returncode}\n\n"
            
            if stdout:
                result += f"STDOUT:\n{stdout}\n"
            
            if stderr:
                result += f"STDERR:\n{stderr}\n"
            
            return result
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout} seconds: {command}"
        except Exception as e:
            return f"Error running command: {str(e)}"


class SystemInfo:
    """Tool for getting system information."""
    
    @staticmethod
    def get_definition() -> Dict[str, Any]:
        """Get tool definition."""
        return {
            "name": "system_info",
            "description": "Get information about the system.",
            "parameters": {
                "type": {
                    "type": "string",
                    "description": "Type of information to get. One of: 'basic', 'env', 'all'."
                }
            },
            "output": "System information of the requested type."
        }
    
    @staticmethod
    def execute(params: Dict[str, Any]) -> str:
        """
        Get system information.
        
        Args:
            params: Dictionary with type of information to get
            
        Returns:
            System information
        """
        info_type = params.get("type", "basic")
        
        result = "System Information:\n\n"
        
        # Basic system info
        if info_type in ["basic", "all"]:
            result += "Basic Information:\n"
            result += f"  OS: {platform.system()} {platform.release()}\n"
            result += f"  Platform: {platform.platform()}\n"
            result += f"  Python: {platform.python_version()}\n"
            result += f"  Machine: {platform.machine()}\n"
            result += f"  Processor: {platform.processor()}\n\n"
        
        # Environment variables
        if info_type in ["env", "all"]:
            result += "Environment Variables:\n"
            for key, value in sorted(os.environ.items()):
                # Skip some overly verbose or sensitive variables
                if key in ["PATH", "LD_LIBRARY_PATH", "PYTHONPATH"] and len(value) > 100:
                    value = value[:100] + "... (truncated)"
                elif "TOKEN" in key or "SECRET" in key or "PASSWORD" in key or "KEY" in key:
                    value = "*** (redacted for security)"
                
                result += f"  {key}: {value}\n"
        
        return result 