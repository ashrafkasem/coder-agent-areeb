#!/bin/bash
set -e

# Deploy script for LLM Tool Agent Server
# This script helps set up and run the server on a remote machine

# Configuration (override these with environment variables)
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"
export MODEL_PATH="${MODEL_PATH:-mistralai/Mistral-7B-Instruct-v0.2}"
export MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-1024}"

# Check if an API key is provided or generate one
if [ -z "$INITIAL_API_KEY" ]; then
    # Generate a secure random API key if none provided
    export INITIAL_API_KEY=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)
    echo "Generated new API key: $INITIAL_API_KEY"
    echo "Store this key securely! You'll need it to access the API."
    
    # Save to a file for reference
    echo "$INITIAL_API_KEY" > .api_key
    echo "API key saved to .api_key file"
    
    echo "You can import this API key into your client with:"
    echo "export LLM_AGENT_API_KEY=$INITIAL_API_KEY"
    echo "export LLM_AGENT_API_URL=http://$(hostname -I | awk '{print $1}'):$PORT"
else
    echo "Using provided API key from environment"
fi

# Create python virtual environment if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv || { echo "ERROR: Failed to create venv. You may need to install python3-venv (e.g. sudo apt install python3-venv)"; exit 1; }
fi

# Activate virtual environment (use . for POSIX portability)
. venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create data directory if needed
if [ ! -d "data" ]; then
    mkdir -p data
fi

# Run the server
echo "Starting LLM Tool Agent Server..."
echo "Model: $MODEL_PATH"
echo "Host: $HOST:$PORT"
echo "To stop the server, press Ctrl+C"

# Run with proper network binding
python -m llm_agent.server

# Deactivate virtual environment on exit
deactivate