# Makefile for LLM Tool Agent

# Default values
MODEL_PATH ?= mistralai/Mistral-7B-Instruct-v0.2
PORT ?= 8000
MAX_NEW_TOKENS ?= 1024

# Use Docker Compose V2 for all docker commands
DOCKER_COMPOSE = docker compose

.PHONY: help run run-docker build-docker clean

help:
	@echo "LLM Tool Agent - Commands:"
	@echo "  make run                  - Run the agent locally with default model"
	@echo "  make run MODEL_PATH=...   - Run with a specific model"
	@echo "  make build-docker         - Build Docker image with default model"
	@echo "  make build-docker MODEL_PATH=... - Build with a specific model"
	@echo "  make run-docker           - Run Docker container with default model"
	@echo "  make run-docker MODEL_PATH=... - Run with a specific model"
	@echo "  make clean                - Clean Python cache files"
	@echo ""
	@echo "Examples:"
	@echo "  make run MODEL_PATH=mistralai/Mixtral-8x7B-Instruct-v0.1"
	@echo "  make build-docker MODEL_PATH=codellama/CodeLlama-7b-Instruct-hf PREDOWNLOAD_MODEL=true"
	@echo "  make run-docker MODEL_PATH=meta-llama/Llama-2-7b-chat-hf"

# Run locally
run:
	MODEL_PATH=$(MODEL_PATH) PORT=$(PORT) MAX_NEW_TOKENS=$(MAX_NEW_TOKENS) ./run_agent.sh

# Build Docker image
build-docker:
	$(DOCKER_COMPOSE) build \
		--build-arg DEFAULT_MODEL_PATH=$(MODEL_PATH) \
		--build-arg DEFAULT_MAX_NEW_TOKENS=$(MAX_NEW_TOKENS) \
		--build-arg PREDOWNLOAD_MODEL=$(PREDOWNLOAD_MODEL)

# Run Docker container
run-docker:
	MODEL_PATH=$(MODEL_PATH) PORT=$(PORT) MAX_NEW_TOKENS=$(MAX_NEW_TOKENS) $(DOCKER_COMPOSE) up

# Clean
clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete