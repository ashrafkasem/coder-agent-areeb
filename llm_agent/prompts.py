"""
Prompt templates for ReAct-style tool use with language models.
"""

from typing import Dict, List, Any, Optional


def get_system_prompt(tools: List[Dict[str, Any]]) -> str:
    """
    Generate the system prompt with available tools.
    
    Args:
        tools: List of tool definitions
        
    Returns:
        Formatted system prompt
    """
    tool_descriptions = "\n\n".join([
        f"Tool: {tool['name']}\n"
        f"Description: {tool['description']}\n"
        f"Parameters: {tool['parameters']}\n"
        f"Output: {tool['output']}"
        for tool in tools
    ])
    
    return f"""You are an AI assistant that can use tools to answer questions. 
When you need to use a tool, format your response using the specific syntax below.
First, think step by step about how to solve the problem, then decide if you need to use a tool.

Available tools:
{tool_descriptions}

To use a tool, respond with:
THINKING: Think step by step about what you need to do.
ACTION: <tool_name>
ACTION_INPUT: {{
  "parameter1": "value1",
  "parameter2": "value2"
}}

When you receive the result from a tool, continue with:
OBSERVATION: <result from the tool>
THINKING: Think about what the result means and what to do next.

If you need to use multiple tools, repeat the ACTION/ACTION_INPUT/OBSERVATION sequence.
When you have the final answer and don't need any more tools, respond with:
FINAL_ANSWER: your detailed final answer

Remember:
1. Follow the exact format for tool use
2. Think through the problem carefully before using tools
3. Always use proper JSON for ACTION_INPUT
4. Don't make up tool results or guess what a tool would return
5. Use only the tools described above
"""


def format_user_query(query: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Format the user query with optional conversation history.
    
    Args:
        query: The current user query
        conversation_history: Optional conversation history
        
    Returns:
        Formatted user prompt
    """
    history_text = ""
    if conversation_history:
        for turn in conversation_history:
            if 'user' in turn:
                history_text += f"User: {turn['user']}\n"
            if 'assistant' in turn:
                history_text += f"Assistant: {turn['assistant']}\n"
    
    return f"{history_text}User: {query}\n\nAssistant:"


def format_react_example(example: Dict[str, str]) -> str:
    """
    Format a ReAct example for few-shot learning.
    
    Args:
        example: Dictionary with keys 'query', 'thinking', 'action', 'action_input',
                'observation', 'final_answer'
                
    Returns:
        Formatted example
    """
    result = f"User: {example['query']}\n\nAssistant: "
    
    if 'thinking' in example and example['thinking']:
        result += f"THINKING: {example['thinking']}\n"
    
    if 'action' in example and example['action']:
        result += f"ACTION: {example['action']}\n"
        result += f"ACTION_INPUT: {example['action_input']}\n"
    
    if 'observation' in example and example['observation']:
        result += f"OBSERVATION: {example['observation']}\n"
    
    if 'final_answer' in example and example['final_answer']:
        result += f"FINAL_ANSWER: {example['final_answer']}\n"
    
    return result


def create_full_prompt(query: str, 
                      tools: List[Dict[str, Any]], 
                      examples: Optional[List[Dict[str, str]]] = None,
                      conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Create the full prompt with system message, few-shot examples, and user query.
    
    Args:
        query: User query
        tools: List of available tools
        examples: Optional list of few-shot examples
        conversation_history: Optional conversation history
        
    Returns:
        Complete formatted prompt
    """
    system_prompt = get_system_prompt(tools)
    
    # Add examples if provided
    examples_text = ""
    if examples:
        examples_text = "\n\n".join([format_react_example(ex) for ex in examples])
        examples_text = f"\n\nHere are some examples of how to use tools:\n\n{examples_text}"
    
    user_prompt = format_user_query(query, conversation_history)
    
    full_prompt = f"{system_prompt}{examples_text}\n\n{user_prompt}"
    return full_prompt 