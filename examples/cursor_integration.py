"""
Example integration with Cursor IDE using the LLM Tool Agent.

This file demonstrates how to use the LLM Tool Agent in the Cursor IDE.
Copy this file to your project and import the `get_agent` function.
"""

import os
import sys
from typing import Optional, Dict, Any

# Add parent directory to Python path to import the client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from llm_agent_client import LLMAgentClient
except ImportError:
    raise ImportError(
        "Could not import LLMAgentClient. Make sure llm_agent_client.py is in your path."
    )


def get_agent(base_url: Optional[str] = None, api_key: Optional[str] = None) -> LLMAgentClient:
    """
    Get a configured LLMAgentClient for use in Cursor IDE.
    
    Args:
        base_url: Optional URL of the LLM Tool Agent server
                 (defaults to LLM_AGENT_API_URL environment variable or http://localhost:8000)
        api_key: Optional API key
                 (defaults to LLM_AGENT_API_KEY environment variable or .api_key file)
    
    Returns:
        Configured LLMAgentClient instance
    """
    try:
        return LLMAgentClient(base_url=base_url, api_key=api_key)
    except Exception as e:
        print(f"Error initializing LLM Agent client: {e}")
        raise


def run_query(query: str, model_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Run a query against the LLM Tool Agent.
    
    Args:
        query: The query to ask the agent
        model_name: Optional model name to use
        
    Returns:
        Response from the agent
    """
    client = get_agent()
    return client.run_agent(query=query, model_name=model_name)


# Example usage
if __name__ == "__main__":
    try:
        # Get the agent
        agent = get_agent()
        
        # Run a test query
        print("Running test query...")
        response = agent.run_agent("What is the current date and time?")
        
        if "final_answer" in response:
            print(f"Agent response: {response['final_answer']}")
        else:
            print("Agent didn't provide a final answer.")
            print(f"Raw response: {response}")
            
        print("\nAgent is ready to use in Cursor IDE!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nTo fix connection issues:")
        print("1. Make sure the LLM Tool Agent server is running")
        print("2. Check that the API key is correct")
        print("3. Verify the server URL (default: http://localhost:8000)")
        
        # Print environment variables for debugging
        print("\nCurrent environment settings:")
        print(f"LLM_AGENT_API_URL: {os.environ.get('LLM_AGENT_API_URL', 'Not set')}")
        print(f"LLM_AGENT_API_KEY: {'Set' if os.environ.get('LLM_AGENT_API_KEY') else 'Not set'}")
        print(f".api_key file exists: {os.path.exists('.api_key')}") 