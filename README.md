# LLM Tool Agent

A lightweight package for using language models (Mistral, GPT, Llama, etc.) with tool use capabilities via ReAct prompting.

## Features

- Run any HuggingFace-compatible language model on GPU
- Support for dynamic model selection
- ReAct prompting structure for tool use
- Extensible tool framework
- Secure API key authentication
- Client-server architecture for remote model serving
- No fine-tuning required

## Deployment Options

### Option 1: Remote Server + Local Client (Recommended)

This approach runs the model on a remote server (with GPU) and lets you use it from any client, including Cursor IDE.

1. **On the remote server (with GPU):**

```bash
# Clone the repository
git clone https://github.com/yourusername/llm-tool-agent.git
cd llm-tool-agent

# Deploy server with automatic API key generation
./deploy_agent_server.sh

# The script will output an API key - save this!
```

2. **On your local machine (Cursor IDE, etc.):**

```python
# Include the standalone client in your project
from llm_agent_client import LLMAgentClient

# Connect to your remote server
client = LLMAgentClient(
    base_url="http://your-server-ip:8000",
    api_key="your-api-key-from-deploy-script"
)

# Use it in your IDE
result = client.run_agent("What is the square root of 16?")
print(result["final_answer"])  # 4
```

### Option 2: Local Server

For development or if you have a local GPU:

```bash
# Run locally with default model
./run.sh

# Or with specific model
MODEL_PATH=mistralai/Mixtral-8x7B-Instruct-v0.1 ./run.sh
```

### Option 3: Docker

For containerized deployment:

```bash
# Build and run with default model
make build-docker
make run-docker

# Or with specific model
make build-docker MODEL_PATH=codellama/CodeLlama-7b-Instruct-hf
```

## Client Options

### Python Integration

For Cursor IDE, Void IDE, or any Python environment:

```python
from llm_agent_client import LLMAgentClient

# Initialize with environment variables
# export LLM_AGENT_API_URL="http://your-server-ip:8000"
# export LLM_AGENT_API_KEY="your-api-key"
client = LLMAgentClient()

# Or provide directly
client = LLMAgentClient(
    base_url="http://your-server:8000",
    api_key="your-api-key"
)

# Run queries
result = client.run_agent("What's the weather in Paris?")
print(result["final_answer"])

# Use specific model
result = client.run_agent(
    "Explain quantum computing", 
    model_name="mistralai/Mixtral-8x7B-Instruct-v0.1"
)

# List available models
models = client.list_models()
print(models)

# List available tools
tools = client.list_tools()
print(tools)
```

### Command Line

```bash
# Using environment variables for connection details
export LLM_AGENT_API_URL="http://your-server:8000"
export LLM_AGENT_API_KEY="your-api-key"

# Run query
python llm_agent_client.py "What's the capital of Japan?"

# Use specific model
python llm_agent_client.py --model mistralai/Mixtral-8x7B-Instruct-v0.1 "Explain quantum computing"
```

## Server API Endpoints

The server provides these HTTP endpoints:

- `POST /agent` - Run agent with a query
- `GET /models` - List loaded models
- `GET /tools` - List available tools
- `POST /api-keys` - Create a new API key
- `GET /api-keys` - List API keys
- `DELETE /api-keys/{key_id}` - Delete an API key

All endpoints require API key authentication via `X-API-Key` header.

## Adding Custom Tools

See the documentation in `llm_agent/tools/README.md` for how to add your own tools.

## Environment Variables

### Server Configuration
- `MODEL_PATH`: HuggingFace model ID or local path to model weights (default: "mistralai/Mistral-7B-Instruct-v0.2")
- `HOST`: Host to bind the server to (default: "0.0.0.0")
- `PORT`: Port to bind the server to (default: 8000)
- `MAX_NEW_TOKENS`: Maximum number of tokens to generate (default: 1024)
- `INITIAL_API_KEY`: Optional predefined API key (auto-generated if not provided)

### Client Configuration
- `LLM_AGENT_API_URL`: URL of the server (default: "http://localhost:8000")
- `LLM_AGENT_API_KEY`: API key for authentication (required)

## Supported Models

The system has been tested with the following models:

- mistralai/Mistral-7B-Instruct-v0.2 (default)
- mistralai/Mixtral-8x7B-Instruct-v0.1
- meta-llama/Llama-2-7b-chat-hf
- codellama/CodeLlama-7b-Instruct-hf
- microsoft/phi-2

You can use any model that is compatible with the HuggingFace Transformers library and follows instruction-tuned formatting. 