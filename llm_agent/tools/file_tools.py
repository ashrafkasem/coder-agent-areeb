"""
File manipulation tools for Mistral Agent.
"""

import os
import json
from typing import Dict, Any, List, Optional
import glob


class FileReader:
    """Tool for reading files."""
    
    @staticmethod
    def get_definition() -> Dict[str, Any]:
        """Get tool definition."""
        return {
            "name": "read_file",
            "description": "Read the contents of a file.",
            "parameters": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read."
                },
                "line_start": {
                    "type": "integer",
                    "description": "Optional line number to start reading from (0-indexed)."
                },
                "line_end": {
                    "type": "integer",
                    "description": "Optional line number to end reading at (0-indexed, inclusive)."
                }
            },
            "output": "The contents of the file, possibly limited to specified lines."
        }
    
    @staticmethod
    def execute(params: Dict[str, Any]) -> str:
        """
        Read the contents of a file.
        
        Args:
            params: Dictionary with file_path and optional line_start and line_end
            
        Returns:
            File contents as a string
        """
        file_path = params.get("file_path")
        line_start = params.get("line_start")
        line_end = params.get("line_end")
        
        if not file_path:
            return "Error: file_path is required"
        
        if not os.path.exists(file_path):
            return f"Error: File not found: {file_path}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if line_start is not None and line_end is not None:
                # Convert to 0-indexed
                line_start = max(0, int(line_start))
                line_end = min(len(lines) - 1, int(line_end))
                content = ''.join(lines[line_start:line_end+1])
                return f"Lines {line_start}-{line_end} from {file_path}:\n{content}"
            else:
                return ''.join(lines)
        except Exception as e:
            return f"Error reading file: {str(e)}"


class FileWriter:
    """Tool for writing to files."""
    
    @staticmethod
    def get_definition() -> Dict[str, Any]:
        """Get tool definition."""
        return {
            "name": "write_file",
            "description": "Write content to a file.",
            "parameters": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to write."
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file."
                },
                "append": {
                    "type": "boolean",
                    "description": "Whether to append to the file instead of overwriting it."
                }
            },
            "output": "Status message indicating success or failure."
        }
    
    @staticmethod
    def execute(params: Dict[str, Any]) -> str:
        """
        Write content to a file.
        
        Args:
            params: Dictionary with file_path, content, and optional append flag
            
        Returns:
            Status message
        """
        file_path = params.get("file_path")
        content = params.get("content")
        append = params.get("append", False)
        
        if not file_path:
            return "Error: file_path is required"
        
        if content is None:
            return "Error: content is required"
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            mode = 'a' if append else 'w'
            with open(file_path, mode, encoding='utf-8') as f:
                f.write(content)
            
            return f"Successfully {'appended to' if append else 'wrote'} {file_path}"
        except Exception as e:
            return f"Error writing to file: {str(e)}"


class ListDirectory:
    """Tool for listing directory contents."""
    
    @staticmethod
    def get_definition() -> Dict[str, Any]:
        """Get tool definition."""
        return {
            "name": "list_directory",
            "description": "List files and directories in a specified path.",
            "parameters": {
                "directory": {
                    "type": "string",
                    "description": "Path to the directory to list."
                },
                "pattern": {
                    "type": "string",
                    "description": "Optional glob pattern to filter results."
                }
            },
            "output": "List of files and directories in the specified path."
        }
    
    @staticmethod
    def execute(params: Dict[str, Any]) -> str:
        """
        List directory contents.
        
        Args:
            params: Dictionary with directory and optional pattern
            
        Returns:
            List of directory contents
        """
        directory = params.get("directory", ".")
        pattern = params.get("pattern", "*")
        
        if not os.path.exists(directory):
            return f"Error: Directory not found: {directory}"
        
        if not os.path.isdir(directory):
            return f"Error: Not a directory: {directory}"
        
        try:
            search_path = os.path.join(directory, pattern)
            items = glob.glob(search_path)
            
            # Separate directories and files
            dirs = []
            files = []
            for item in items:
                if os.path.isdir(item):
                    dirs.append(os.path.basename(item) + "/")
                else:
                    files.append(os.path.basename(item))
            
            # Sort both lists
            dirs.sort()
            files.sort()
            
            # Combine results
            result = f"Contents of {directory} (pattern: {pattern}):\n\n"
            
            if dirs:
                result += "Directories:\n"
                result += "\n".join(dirs) + "\n\n"
            
            if files:
                result += "Files:\n"
                result += "\n".join(files)
            
            if not dirs and not files:
                result += "No items found matching the pattern."
            
            return result
        except Exception as e:
            return f"Error listing directory: {str(e)}" 