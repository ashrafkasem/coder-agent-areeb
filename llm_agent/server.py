"""
FastAPI server for the LLM Tool Agent.
"""

import os
import secrets
import uuid
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
import uvicorn
from loguru import logger
from fastapi.responses import JSONResponse
from fastapi import status
import time

from .agent import ToolAgent
from .model import LLMModel
from .tools.file_tools import FileReader, FileWriter, ListDirectory
from .tools.system_tools import CommandRunner, SystemInfo
from .tools.web_tools import WebSearch, WebPageReader


class AgentQuery(BaseModel):
    """Model for agent query."""
    query: str = Field(..., description="The user query to process")
    model_name: Optional[str] = Field(None, description="Optional model name to use. If not provided, the default or environment variable will be used.")
    tools: Optional[List[str]] = Field(None, description="List of tool names to enable. If not provided, all tools are enabled.")
    conversation_history: Optional[List[Dict[str, str]]] = Field(None, description="Optional conversation history")
    examples: Optional[List[Dict[str, str]]] = Field(None, description="Optional few-shot examples")


class ApiKeyGenerator(BaseModel):
    """Model for API key generation."""
    key_name: str = Field(..., description="A name for the API key")


class ApiKeyResponse(BaseModel):
    """Model for API key response."""
    key_id: str
    key_value: str
    key_name: str


# OpenAI-compatible schemas
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class OpenAIMessage(BaseModel):
    role: str
    content: str
    name: Optional[str] = None

class OpenAIChatRequest(BaseModel):
    model: str
    messages: List[OpenAIMessage]
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Any] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: Optional[bool] = False
    user: Optional[str] = None
    # ... add more OpenAI params as needed

class OpenAIToolCall(BaseModel):
    id: str
    type: str = "function"
    function: Dict[str, Any]

class OpenAIChatResponseChoice(BaseModel):
    index: int
    message: Dict[str, Any]
    finish_reason: Optional[str] = None
    tool_calls: Optional[List[OpenAIToolCall]] = None

class OpenAIChatResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[OpenAIChatResponseChoice]


# Dictionary to cache models
model_cache = {}

# Dictionary to store API keys: {key_value: {"key_id": id, "key_name": name}}
api_keys = {}

# Get API key from environment or generate one
def setup_initial_api_key():
    initial_key = os.environ.get("INITIAL_API_KEY")
    if not initial_key:
        initial_key = secrets.token_urlsafe(32)
        logger.info(f"No INITIAL_API_KEY found in environment. Generated: {initial_key}")
    
    key_id = str(uuid.uuid4())
    api_keys[initial_key] = {"key_id": key_id, "key_name": "initial_key"}
    logger.info(f"Initial API key set up with ID: {key_id}")
    return initial_key


# --- API Key extraction helper ---
def extract_api_key(request: Request) -> Optional[str]:
    """
    Extract API key from X-API-Key or Authorization: Bearer headers.
    """
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            api_key = auth_header[7:].strip()
    return api_key


def verify_api_key(request: Request):
    api_key = extract_api_key(request)
    if not api_key or api_key not in api_keys:
        raise HTTPException(status_code=401, detail="Invalid or missing API key. Provide via 'X-API-Key' or 'Authorization: Bearer <key>' header.")
    return api_keys[api_key]


app = FastAPI(
    title="LLM Tool Agent API",
    description="API for using language models with ReAct-style tool use",
    version="0.1.0"
)


@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    """Middleware to log all requests and check API key."""
    # Log request details
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"Request from {client_host} to {request.url.path}")
    # Allow docs endpoints without auth
    if request.url.path in ["/docs", "/redoc"]:
        return await call_next(request)
    api_key = extract_api_key(request)
    if not api_key:
        logger.warning(f"Request to {request.url.path} rejected: Missing API key header")
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "message": "Authentication required. Add 'X-API-Key' or 'Authorization: Bearer <key>' header with a valid API key. See API_AUTH.md for details."
                }
            }
        )
    response = await call_next(request)
    if response.status_code == 403:
        logger.warning(f"Request to {request.url.path} rejected: Invalid API key")
    return response


@app.on_event("startup")
async def startup_event():
    """Initialize the default model and agent on startup."""
    # Set up initial API key
    initial_key = setup_initial_api_key()
    logger.info(f"Server can be accessed with API key: {initial_key}")
    
    # Initialize the default model
    default_model_id = os.environ.get("MODEL_PATH")
    logger.info(f"Initializing default model: {default_model_id}")
    try:
        model = get_model(default_model_id)
    except Exception as e:
        logger.error(f"Failed to load model '{default_model_id}': {e}")
        raise RuntimeError(f"Failed to load model '{default_model_id}': {e}")
    
    # Initialize the agent with the default model
    logger.info("Initializing agent...")
    agent = ToolAgent(model=model)
    
    # Register all tools
    logger.info("Registering tools...")
    
    # File tools
    file_reader = FileReader()
    agent.register_tool(
        name=file_reader.get_definition()["name"],
        func=file_reader.execute,
        description=file_reader.get_definition()["description"],
        parameters=file_reader.get_definition()["parameters"],
        output_description=file_reader.get_definition()["output"]
    )
    
    file_writer = FileWriter()
    agent.register_tool(
        name=file_writer.get_definition()["name"],
        func=file_writer.execute,
        description=file_writer.get_definition()["description"],
        parameters=file_writer.get_definition()["parameters"],
        output_description=file_writer.get_definition()["output"]
    )
    
    list_directory = ListDirectory()
    agent.register_tool(
        name=list_directory.get_definition()["name"],
        func=list_directory.execute,
        description=list_directory.get_definition()["description"],
        parameters=list_directory.get_definition()["parameters"],
        output_description=list_directory.get_definition()["output"]
    )
    
    # System tools
    command_runner = CommandRunner()
    agent.register_tool(
        name=command_runner.get_definition()["name"],
        func=command_runner.execute,
        description=command_runner.get_definition()["description"],
        parameters=command_runner.get_definition()["parameters"],
        output_description=command_runner.get_definition()["output"]
    )
    
    system_info = SystemInfo()
    agent.register_tool(
        name=system_info.get_definition()["name"],
        func=system_info.execute,
        description=system_info.get_definition()["description"],
        parameters=system_info.get_definition()["parameters"],
        output_description=system_info.get_definition()["output"]
    )
    
    # Web tools
    web_search = WebSearch()
    agent.register_tool(
        name=web_search.get_definition()["name"],
        func=web_search.execute,
        description=web_search.get_definition()["description"],
        parameters=web_search.get_definition()["parameters"],
        output_description=web_search.get_definition()["output"]
    )
    
    web_page_reader = WebPageReader()
    agent.register_tool(
        name=web_page_reader.get_definition()["name"],
        func=web_page_reader.execute,
        description=web_page_reader.get_definition()["description"],
        parameters=web_page_reader.get_definition()["parameters"],
        output_description=web_page_reader.get_definition()["output"]
    )
    
    # Store the agent in the app state for default use
    app.state.default_agent = agent
    logger.info("Agent initialized with all tools registered")


@app.post("/agent", dependencies=[Depends(verify_api_key)])
async def run_agent(query: AgentQuery):
    """
    Run the agent with a query.
    
    Args:
        query: The query details
        
    Returns:
        Agent results
    """
    # Use the specified model or default to the pre-loaded one
    if query.model_name:
        model = get_model(query.model_name)
        agent = ToolAgent(model=model)
        
        # Copy tools from the default agent
        for tool_def in app.state.default_agent.tool_definitions:
            tool_name = tool_def["name"]
            agent.register_tool(
                name=tool_name,
                func=app.state.default_agent.tools[tool_name],
                description=tool_def["description"],
                parameters=tool_def["parameters"],
                output_description=tool_def["output"]
            )
    else:
        agent = app.state.default_agent
    
    # Filter tools if specified
    if query.tools:
        filtered_tools = []
        all_tools = {tool["name"]: tool for tool in agent.tool_definitions}
        
        for tool_name in query.tools:
            if tool_name in all_tools:
                filtered_tools.append(all_tools[tool_name])
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Tool '{tool_name}' not found. Available tools: {', '.join(all_tools.keys())}"
                )
        
        # Store original tools and temporarily replace with filtered tools
        original_tool_definitions = agent.tool_definitions
        agent.tool_definitions = filtered_tools
    else:
        original_tool_definitions = None
    
    try:
        result = agent.run(
            query=query.query,
            conversation_history=query.conversation_history,
            examples=query.examples
        )
        
        # Add model information to the result
        result["model_used"] = agent.model.model_id
        
        return result
    finally:
        # Restore original tools if we filtered them
        if query.tools and original_tool_definitions:
            agent.tool_definitions = original_tool_definitions


@app.post("/api-keys", dependencies=[Depends(verify_api_key)])
async def create_api_key(key_request: ApiKeyGenerator):
    """
    Create a new API key.
    
    Args:
        key_request: The key generation request
        
    Returns:
        The generated API key
    """
    key_value = secrets.token_urlsafe(32)
    key_id = str(uuid.uuid4())
    key_name = key_request.key_name
    
    api_keys[key_value] = {"key_id": key_id, "key_name": key_name}
    
    return ApiKeyResponse(key_id=key_id, key_value=key_value, key_name=key_name)


@app.get("/api-keys", dependencies=[Depends(verify_api_key)])
async def list_api_keys():
    """
    List all API keys (without revealing the actual key values).
    
    Returns:
        List of API key information
    """
    key_info = []
    for key_value, info in api_keys.items():
        # Only return the last 4 characters of the key
        masked_key = "••••" + key_value[-4:]
        key_info.append({
            "key_id": info["key_id"],
            "key_name": info["key_name"],
            "masked_key": masked_key
        })
    
    return {"api_keys": key_info}


@app.delete("/api-keys/{key_id}", dependencies=[Depends(verify_api_key)])
async def delete_api_key(key_id: str):
    """
    Delete an API key.
    
    Args:
        key_id: The key ID to delete
        
    Returns:
        Success message
    """
    # Find the key with the given ID
    key_to_delete = None
    for key_value, info in api_keys.items():
        if info["key_id"] == key_id:
            key_to_delete = key_value
            break
    
    if not key_to_delete:
        raise HTTPException(status_code=404, detail="API key not found")
    
    # Delete the key
    del api_keys[key_to_delete]
    
    return {"status": "success", "message": "API key deleted"}


@app.get("/models", dependencies=[Depends(verify_api_key)])
async def list_models():
    """
    List all loaded models.
    
    Returns:
        List of loaded models
    """
    return {"models": list(model_cache.keys())}


@app.get("/tools", dependencies=[Depends(verify_api_key)])
async def list_tools():
    """
    List all available tools.
    
    Returns:
        List of available tools
    """
    agent = app.state.default_agent
    return {"tools": agent.tool_definitions}


@app.get("/", dependencies=[Depends(verify_api_key)])
async def root():
    """
    Root endpoint with basic information.
    
    Returns:
        Basic API information
    """
    return {
        "name": "LLM Tool Agent API",
        "version": "0.1.0",
        "description": "API for using language models with ReAct-style tool use",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "This information"},
            {"path": "/models", "method": "GET", "description": "List all loaded models"},
            {"path": "/tools", "method": "GET", "description": "List all available tools"},
            {"path": "/agent", "method": "POST", "description": "Run the agent with a query"},
            {"path": "/api-keys", "method": "POST", "description": "Create a new API key"},
            {"path": "/api-keys", "method": "GET", "description": "List all API keys"},
            {"path": "/api-keys/{key_id}", "method": "DELETE", "description": "Delete an API key"}
        ]
    }


@app.post("/v1/chat/completions", dependencies=[Depends(verify_api_key)])
async def openai_chat_completions(request: OpenAIChatRequest):
    """
    OpenAI-compatible chat completions endpoint with tool use support (tool_call).
    """
    # Map OpenAI messages to agent query and conversation history
    conversation = []
    user_query = None
    for msg in request.messages:
        if msg.role == "user":
            user_query = msg.content
        elif msg.role == "assistant":
            conversation.append({"assistant": msg.content})
        elif msg.role == "system":
            pass
        elif msg.role == "tool":
            # Optionally handle tool messages
            pass
    if not user_query:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": {"message": "No user message found"}})

    # Use requested model or default
    model_name = request.model if request.model else os.environ.get("MODEL_PATH")
    model = get_model(model_name)
    agent = ToolAgent(model=model)
    for tool_def in app.state.default_agent.tool_definitions:
        tool_name = tool_def["name"]
        agent.register_tool(
            name=tool_name,
            func=app.state.default_agent.tools[tool_name],
            description=tool_def["description"],
            parameters=tool_def["parameters"],
            output_description=tool_def["output"]
        )
    # Run the agent
    result = agent.run(query=user_query, conversation_history=conversation)

    # If tool use is requested, return tool_calls in OpenAI format
    tool_calls = []
    if result.get("actions"):
        for i, action in enumerate(result["actions"]):
            if action.get("tool") and action.get("input") is not None:
                tool_calls.append(OpenAIToolCall(
                    id=f"call_{i}",
                    function={
                        "name": action["tool"],
                        "arguments": action["input"]
                    }
                ))

    response = OpenAIChatResponse(
        id="chatcmpl-" + str(uuid.uuid4()),
        object="chat.completion",
        created=int(time.time()),
        model=model_name,
        choices=[
            OpenAIChatResponseChoice(
                index=0,
                message={
                    "role": "assistant",
                    "content": result.get("final_answer", "")
                },
                finish_reason="stop",
                tool_calls=tool_calls if tool_calls else None
            )
        ]
    )
    logger.info(f"Returning OpenAI response: {response.model_dump_json()}")
    return response.model_dump()  # For Pydantic v2; use response.dict() for v1


@app.get("/v1/models", dependencies=[Depends(verify_api_key)])
async def openai_list_models():
    """
    OpenAI-compatible models endpoint.
    """
    models = list(model_cache.keys())
    if not models:
        # If no models loaded yet, show default
        models = [os.environ.get("MODEL_PATH", "mistralai/Mistral-7B-Instruct-v0.2")]
    return {
        "object": "list",
        "data": [
            {"id": m, "object": "model", "created": 0, "owned_by": "user"} for m in models
        ]
    }


def get_model(model_name: Optional[str] = None):
    """
    Get or create a model instance.
    Args:
        model_name: Optional model name or HF model ID
    Returns:
        LLMModel instance
    """
    model_id = model_name or os.environ.get("MODEL_PATH")
    if not model_id:
        raise RuntimeError("No model name provided and MODEL_PATH is not set.")
    if model_id in model_cache:
        logger.info(f"Using cached model: {model_id}")
        return model_cache[model_id]
    logger.info(f"Initializing new model: {model_id}")
    model = LLMModel(model_id=model_id)
    model_cache[model_id] = model
    return model


def main():
    """Run the server."""
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()