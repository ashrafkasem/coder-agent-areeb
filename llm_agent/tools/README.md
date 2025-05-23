# Creating Custom Tools

This document explains how to create custom tools for the Mistral Agent.

## Tool Structure

Each tool should be a class with two static methods:

1. `get_definition()` - returns the tool definition
2. `execute(params)` - executes the tool with the given parameters

## Example Tool

Here's a simple example of a custom tool:

```python
class MyCustomTool:
    """My custom tool description."""
    
    @staticmethod
    def get_definition() -> Dict[str, Any]:
        """Get tool definition."""
        return {
            "name": "my_custom_tool",
            "description": "A description of what my tool does.",
            "parameters": {
                "param1": {
                    "type": "string",
                    "description": "The first parameter."
                },
                "param2": {
                    "type": "integer",
                    "description": "The second parameter."
                }
            },
            "output": "Description of the tool's output."
        }
    
    @staticmethod
    def execute(params: Dict[str, Any]) -> str:
        """
        Execute the tool.
        
        Args:
            params: Dictionary with parameters
            
        Returns:
            Tool result as a string
        """
        param1 = params.get("param1")
        param2 = params.get("param2")
        
        # Validate parameters
        if not param1:
            return "Error: param1 is required"
        
        # Do something with the parameters
        result = f"Processing {param1} with {param2}"
        
        return result
```

## Registering Your Tool

Once you've created your tool, you need to register it with the agent:

```python
from mistral_agent.agent import ToolAgent
from my_tools import MyCustomTool

# Create the agent
agent = ToolAgent()

# Register your tool
agent.register_tool(
    name=MyCustomTool.get_definition()["name"],
    func=MyCustomTool.execute,
    description=MyCustomTool.get_definition()["description"],
    parameters=MyCustomTool.get_definition()["parameters"],
    output_description=MyCustomTool.get_definition()["output"]
)
```

## Tool Design Guidelines

1. **Error Handling**: Always handle exceptions and return clear error messages
2. **Validation**: Validate all parameters before use
3. **Security**: Be cautious with file paths, commands, and URLs
4. **Documentation**: Clearly document what your tool does and what inputs it expects
5. **Determinism**: Tools should be as deterministic as possible
6. **Permissions**: Consider what permissions your tool needs
7. **Output Format**: Return results as formatted strings that are easy to read

## Parameter Types

The agent supports these parameter types:

- `string`: Text
- `integer`: Whole numbers
- `number`: Floating point numbers
- `boolean`: True/false values
- `array`: Lists
- `object`: Nested objects

## Examples

The `tools` directory contains several example tools:

- `file_tools.py`: Tools for reading and writing files
- `system_tools.py`: Tools for running commands and getting system info
- `web_tools.py`: Tools for web search and fetching web pages 