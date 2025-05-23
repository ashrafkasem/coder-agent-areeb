"""
LLM Tool Agent Client - For connecting to remote LLM Tool Agent server.

This standalone client can be imported in any environment (Cursor IDE, etc.)
to access a remotely running LLM Tool Agent server.

Usage:
    from llm_agent_client import LLMAgentClient
    
    client = LLMAgentClient(
        base_url="http://your-server:8000",
        api_key="your-api-key"
    )
    
    # Run a query
    result = client.run_agent("What is the square root of 16?")
    print(result["final_answer"])
    
    # List available models
    models = client.list_models()
    print(models)
    
    # Use a specific model
    result = client.run_agent(
        "What is the capital of France?",
        model_name="mistralai/Mixtral-8x7B-Instruct-v0.1"
    )
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional, Union


class LLMAgentClient:
    """Client for interacting with a remote LLM Tool Agent server."""
    
    @staticmethod
    def load_api_key_from_file(path: str = ".api_key") -> Optional[str]:
        """
        Load API key from a file if present.
        """
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read().strip()
        return None
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the LLM agent client.
        
        Args:
            base_url: Base URL of the LLM Tool Agent server
                     (defaults to LLM_AGENT_API_URL environment variable or http://localhost:8000)
            api_key: API key for accessing the server
                     (defaults to LLM_AGENT_API_KEY environment variable)
        """
        self.base_url = base_url or os.environ.get("LLM_AGENT_API_URL", "http://localhost:8000")
        self.api_key = api_key or os.environ.get("LLM_AGENT_API_KEY")
        
        if not self.api_key:
            self.api_key = self.load_api_key_from_file()
        if not self.api_key:
            raise ValueError("API key is required. Provide it directly, via LLM_AGENT_API_KEY, or in a .api_key file.")
        
        # Remove trailing slash if present
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]
            
        # Default headers
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def run_agent(
        self,
        query: str,
        model_name: Optional[str] = None,
        tools: Optional[List[str]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Run the agent with a query.
        
        Args:
            query: The user query
            model_name: Optional model name or HuggingFace model ID to use
            tools: Optional list of tool names to enable
            conversation_history: Optional conversation history
            examples: Optional few-shot examples
            
        Returns:
            Agent results
        """
        payload = {"query": query}
        
        if model_name:
            payload["model_name"] = model_name
        
        if tools:
            payload["tools"] = tools
        
        if conversation_history:
            payload["conversation_history"] = conversation_history
        
        if examples:
            payload["examples"] = examples
        
        response = requests.post(
            f"{self.base_url}/agent",
            headers=self.headers,
            json=payload
        )
        self._check_response(response)
        
        return response.json()
    
    def list_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all available tools.
        
        Returns:
            List of available tools
        """
        response = requests.get(
            f"{self.base_url}/tools",
            headers=self.headers
        )
        self._check_response(response)
        
        return response.json()
    
    def list_models(self) -> Dict[str, List[str]]:
        """
        List all loaded models.
        
        Returns:
            List of loaded models
        """
        response = requests.get(
            f"{self.base_url}/models",
            headers=self.headers
        )
        self._check_response(response)
        
        return response.json()
    
    def create_api_key(self, key_name: str) -> Dict[str, str]:
        """
        Create a new API key.
        
        Args:
            key_name: A name for the API key
            
        Returns:
            The generated API key information
        """
        response = requests.post(
            f"{self.base_url}/api-keys",
            headers=self.headers,
            json={"key_name": key_name}
        )
        self._check_response(response)
        
        return response.json()
    
    def list_api_keys(self) -> Dict[str, List[Dict[str, str]]]:
        """
        List all API keys.
        
        Returns:
            List of API key information
        """
        response = requests.get(
            f"{self.base_url}/api-keys",
            headers=self.headers
        )
        self._check_response(response)
        
        return response.json()
    
    def delete_api_key(self, key_id: str) -> Dict[str, str]:
        """
        Delete an API key.
        
        Args:
            key_id: The key ID to delete
            
        Returns:
            Success message
        """
        response = requests.delete(
            f"{self.base_url}/api-keys/{key_id}",
            headers=self.headers
        )
        self._check_response(response)
        
        return response.json()
    
    def _check_response(self, response: requests.Response) -> None:
        """
        Check the response for errors.
        
        Args:
            response: Response object
            
        Raises:
            Exception if the response status code is not 2xx
        """
        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_message = error_data.get("detail", "Unknown error")
            except:
                error_message = response.text or f"HTTP Error {response.status_code}"
            
            raise Exception(f"API Error: {error_message}")


# Example usage
if __name__ == "__main__":
    import sys
    
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python llm_agent_client.py 'Your query'")
        sys.exit(1)
    
    query = sys.argv[1]
    model_arg = None
    
    # Check for --model flag
    if len(sys.argv) > 3 and sys.argv[1] == "--model":
        model_arg = sys.argv[2]
        query = sys.argv[3]
    
    try:
        # Create client
        client = LLMAgentClient()
        
        # List available models
        models = client.list_models()
        print("Available models:")
        for model in models.get("models", []):
            print(f"  - {model}")
        print()
        
        # Run the agent
        print(f"Query: {query}")
        if model_arg:
            print(f"Using model: {model_arg}")
        
        result = client.run_agent(query, model_name=model_arg)
        
        # Print the result
        print(f"\nModel used: {result.get('model_used', 'unknown')}")
        
        if result.get('thinking'):
            print("\nThinking:")
            for i, thought in enumerate(result['thinking'], 1):
                print(f"{i}. {thought}")
        
        if result.get('actions'):
            print("\nActions:")
            for i, action in enumerate(result['actions'], 1):
                print(f"{i}. Tool: {action['tool']}")
                print(f"   Input: {json.dumps(action['input'])}")
                print(f"   Observation: {action['observation']}")
        
        if result.get('final_answer'):
            print("\nFinal Answer:")
            print(result['final_answer'])
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)