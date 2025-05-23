#!/bin/bash
set -e

# Default values (can be overridden by environment variables)
HF_TOKEN=${HUGGINGFACE_TOKEN:-""}
MODEL=${MODEL_PATH:-"mistralai/Mistral-7B-Instruct-v0.2"}
PORT=${PORT:-8000}

# Check for required Hugging Face token
if [ -z "$HF_TOKEN" ]; then
    echo "ERROR: HUGGINGFACE_TOKEN is required for accessing gated models"
    echo "Usage: HUGGINGFACE_TOKEN=your_token ./run_docker.sh"
    echo "   or: export HUGGINGFACE_TOKEN=your_token first"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if the image exists, build if needed
if ! docker image inspect llm-agent &> /dev/null; then
    echo "Docker image 'llm-agent' not found. Building it now..."
    docker build -t llm-agent .
fi

echo "Starting LLM Agent Docker container with model: $MODEL"
echo "Server will be available at http://localhost:$PORT"

# Run the container
docker run --gpus all \
  -e HUGGINGFACE_TOKEN="$HF_TOKEN" \
  -e MODEL_PATH="$MODEL" \
  -e MAX_NEW_TOKENS=1024 \
  -e HOST=0.0.0.0 \
  -e PORT=$PORT \
  -p $PORT:$PORT \
  -v $(pwd)/data:/app/data \
  -v huggingface-cache:/root/.cache/huggingface \
  llm-agent

# Note: The container will continue running until you press Ctrl+C 