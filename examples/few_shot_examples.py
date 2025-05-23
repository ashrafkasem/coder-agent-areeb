"""
Few-shot examples for better tool use with Mistral Agent.
"""

from typing import List, Dict, Any

# Example demonstrating the use of file tools
FILE_TOOL_EXAMPLE = {
    "query": "What files are in the current directory and create a summary.txt file with the list?",
    "thinking": "I need to list the files in the current directory first, then create a file with that information.",
    "action": "list_directory",
    "action_input": {
        "directory": "."
    },
    "observation": "Contents of . (pattern: *):\n\nDirectories:\ndir1/\ndir2/\n\nFiles:\nfile1.txt\nfile2.py\nREADME.md",
    "final_answer": "I've checked the current directory and created a summary.txt file. The directory contains the following files and directories:\n\nDirectories: dir1, dir2\nFiles: file1.txt, file2.py, README.md"
}

# Example demonstrating the use of command execution
COMMAND_TOOL_EXAMPLE = {
    "query": "What is the current date and time?",
    "thinking": "I need to run a command to get the current date and time on the system.",
    "action": "run_command",
    "action_input": {
        "command": "date"
    },
    "observation": "Command: date\nExit code: 0\n\nSTDOUT:\nMon Oct 16 14:23:45 UTC 2023\n",
    "final_answer": "The current date and time is: Monday, October 16, 2023, 14:23:45 UTC."
}

# Example demonstrating the use of web search
WEB_SEARCH_EXAMPLE = {
    "query": "What is the capital of France?",
    "thinking": "I need to search for information about the capital of France.",
    "action": "web_search",
    "action_input": {
        "query": "capital of France"
    },
    "observation": "Search results for: 'capital of France'\n\n1. Capital of France\n   Paris is the capital city of France, located in the north-central part of the country.\n   URL: https://example.com/result1?q=capital%20of%20France\n\n2. France - Wikipedia\n   Paris is the capital and most populous city of France.\n   URL: https://example.com/result2?q=capital%20of%20France\n\nNote: These are mock results. To use real search results, integrate with a search API.",
    "final_answer": "The capital of France is Paris."
}


def get_examples(tool_types: List[str] = None) -> List[Dict[str, Any]]:
    """
    Get few-shot examples filtered by tool types.
    
    Args:
        tool_types: Optional list of tool types to filter by
                   (options: 'file', 'command', 'web')
        
    Returns:
        List of few-shot examples
    """
    all_examples = {
        "file": FILE_TOOL_EXAMPLE,
        "command": COMMAND_TOOL_EXAMPLE,
        "web": WEB_SEARCH_EXAMPLE
    }
    
    if not tool_types:
        # Return all examples if no filter is specified
        return list(all_examples.values())
    
    filtered_examples = []
    for tool_type in tool_types:
        if tool_type in all_examples:
            filtered_examples.append(all_examples[tool_type])
    
    return filtered_examples


# Example usage
if __name__ == "__main__":
    from client import run_agent
    
    # Get all examples
    examples = get_examples()
    
    # Run the agent with examples
    result = run_agent(
        query="What's in my documents folder and how many files are there?",
        examples=examples
    )
    
    # Print the result
    print(f"Query: {result['query']}")
    print(f"Final Answer: {result['final_answer']}") 