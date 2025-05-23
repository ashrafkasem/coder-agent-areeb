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

### Option 3: Docker (Recommended)

For containerized deployment, use the provided Docker script:

```bash
# Set your Hugging Face token (required for gated models like Mistral)
export HUGGINGFACE_TOKEN=your_token_here

# Run with default model
./run_docker.sh

# Or specify a different model
MODEL_PATH=microsoft/phi-2 ./run_docker.sh
```

This script will:
1. Build the Docker image if needed
2. Run the container with GPU support
3. Mount the data directory and HuggingFace cache
4. Pass your Hugging Face token for authentication

> **Note**: For models that require authentication (like Mistral), you need a valid Hugging Face token with proper permissions. Get one at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).

If you prefer manual Docker commands:

```bash
# Build the image
docker build -t llm-agent .

# Run the container
docker run --gpus all \
  -e HUGGINGFACE_TOKEN=your_token_here \
  -e MODEL_PATH=mistralai/Mistral-7B-Instruct-v0.2 \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v huggingface-cache:/root/.cache/huggingface \
  llm-agent
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

## API Key Usage

- The server will generate and print an API key on first run. This key is also saved to a `.api_key` file in the server directory.
- All client requests (including from Cursor, Continue, or the provided Python client) **must** include the API key in the `X-API-Key` header. The example clients now support loading the key from the `.api_key` file or the `LLM_AGENT_API_KEY` environment variable.
- If you copy the `.api_key` file to your local machine, you can use the provided example client or `llm_agent_client.py` without manually setting the environment variable.

## Quickstart for Remote Use

1. **Deploy the server on your remote machine:**

```bash
./deploy_agent_server.sh
```

2. **Copy the `.api_key` file to your local machine.**

3. **Use the Python client in your IDE or script:**

```python
from llm_agent_client import LLMAgentClient
client = LLMAgentClient(base_url="http://your-server-ip:8000")
result = client.run_agent("What is the square root of 16?")
print(result["final_answer"])
```

The client will automatically use the API key from `.api_key` if present, or from the `LLM_AGENT_API_KEY` environment variable.

## Hugging Face Authentication

Many modern LLMs (like Mistral) require authentication to download. To use these models:

1. Create a Hugging Face account at [huggingface.co](https://huggingface.co)
2. Generate a token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
3. Request access to the model (e.g., visit [mistralai/Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) and click "Access repository")
4. Set the `HUGGINGFACE_TOKEN` environment variable:
   ```bash
   export HUGGINGFACE_TOKEN=your_token_here
   ```

The system will automatically use this token when loading models.

For open-access models like Microsoft's Phi-2, authentication is not required.