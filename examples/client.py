"""
Sample client for the Mistral Tool Agent API.
"""

import sys
import json
import requests
import os
from typing import Dict, Any, List, Optional


def get_api_key() -> str:
    """
    Get API key from environment or .api_key file.
    """
    api_key = os.environ.get("LLM_AGENT_API_KEY")
    if not api_key and os.path.exists(".api_key"):
        with open(".api_key", "r") as f:
            api_key = f.read().strip()
    if not api_key:
        raise RuntimeError("API key not found. Set LLM_AGENT_API_KEY or place it in .api_key file.")
    return api_key


def run_agent(
    query: str,
    model_name: Optional[str] = None,
    tools: Optional[List[str]] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    examples: Optional[List[Dict[str, str]]] = None,
    api_url: str = "http://localhost:8000"
) -> Dict[str, Any]:
    """
    Run the agent with a query.
    
    Args:
        query: The user query
        model_name: Optional model name or HuggingFace model ID to use
        tools: Optional list of tool names to enable
        conversation_history: Optional conversation history
        examples: Optional few-shot examples
        api_url: The base URL of the API
        
    Returns:
        Agent results
    """
    payload = {
        "query": query
    }
    
    if model_name:
        payload["model_name"] = model_name
    
    if tools:
        payload["tools"] = tools
    
    if conversation_history:
        payload["conversation_history"] = conversation_history
    
    if examples:
        payload["examples"] = examples
    
    response = requests.post(f"{api_url}/agent", json=payload, headers={"X-API-Key": get_api_key()})
    response.raise_for_status()
    
    return response.json()


def list_tools(api_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """
    List all available tools.
    
    Args:
        api_url: The base URL of the API
        
    Returns:
        List of available tools
    """
    response = requests.get(f"{api_url}/tools", headers={"X-API-Key": get_api_key()})
    response.raise_for_status()
    
    return response.json()


def list_models(api_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """
    List all loaded models.
    
    Args:
        api_url: The base URL of the API
        
    Returns:
        List of loaded models
    """
    response = requests.get(f"{api_url}/models", headers={"X-API-Key": get_api_key()})
    response.raise_for_status()
    
    return response.json()


def main():
    """Run the client example."""
    api_url = "http://localhost:8000"
    
    # Parse command-line arguments
    model_name = None
    query = "What files are in the current directory?"
    
    if len(sys.argv) > 1:
        # Check if first argument is a model name flag
        if sys.argv[1] == "--model" and len(sys.argv) > 2:
            model_name = sys.argv[2]
            # If there's a query after the model flag
            if len(sys.argv) > 3:
                query = sys.argv[3]
        else:
            # First argument is the query
            query = sys.argv[1]
    
    # List available models (if any are loaded)
    try:
        models_response = list_models(api_url)
        if models_response["models"]:
            print("Available models:")
            for model_id in models_response["models"]:
                print(f"  - {model_id}")
            print()
    except Exception as e:
        print(f"Error fetching models: {e}")
    
    # List available tools
    try:
        tools_response = list_tools(api_url)
        tool_names = [tool["name"] for tool in tools_response["tools"]]
        print(f"Available tools: {', '.join(tool_names)}")
        print()
    except Exception as e:
        print(f"Error fetching tools: {e}")
    
    # Run the agent with the query
    print(f"Running agent with query: '{query}'")
    if model_name:
        print(f"Using model: {model_name}")
    
    result = run_agent(query, model_name=model_name, api_url=api_url)
    
    # Print the result
    print("\nAgent result:")
    print(f"Query: {result['query']}")
    print(f"Model used: {result.get('model_used', 'unknown')}")
    
    if result['thinking']:
        print("\nThinking:")
        for i, thought in enumerate(result['thinking'], 1):
            print(f"{i}. {thought}")
    
    if result['actions']:
        print("\nActions:")
        for i, action in enumerate(result['actions'], 1):
            print(f"{i}. Tool: {action['tool']}")
            print(f"   Input: {json.dumps(action['input'])}")
            print(f"   Observation: {action['observation']}")
    
    if result['final_answer']:
        print("\nFinal Answer:")
        print(result['final_answer'])


if __name__ == "__main__":
    main()