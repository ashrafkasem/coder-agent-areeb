#!/bin/bash

# Run script for LLM Tool Agent
# This script helps quickly start the server locally

# Configuration (override these with environment variables)
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"
export MODEL_PATH="${MODEL_PATH:-mistralai/Mistral-7B-Instruct-v0.2}"
export MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-1024}"

# Get API key from environment or generate one
if [ -z "$INITIAL_API_KEY" ]; then
    export INITIAL_API_KEY=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)
    echo "Generated API key: $INITIAL_API_KEY"
else
    echo "Using API key from environment"
fi

# Create python virtual environment if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the server
echo "Starting LLM Tool Agent on $HOST:$PORT"
echo "Model: $MODEL_PATH"
echo "To use the API, include this header in your requests:"
echo "X-API-Key: $INITIAL_API_KEY"
echo ""
echo "To stop the server, press Ctrl+C"

# Run with proper module path
python -m llm_agent.server

# Deactivate virtual environment on exit
deactivate 