FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

WORKDIR /app

# Install Python and other dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 python3-pip python3-dev \
    build-essential git curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set Python default to Python 3
RUN ln -sf /usr/bin/python3 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# Copy requirements first for better layer caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . /app/

# Set build arguments with defaults
ARG DEFAULT_MODEL_PATH=mistralai/Mistral-7B-Instruct-v0.2
ARG DEFAULT_MAX_NEW_TOKENS=1024
ARG DEFAULT_HOST=0.0.0.0
ARG DEFAULT_PORT=8000

# Set environment variables with build arg defaults
ENV HOST=${DEFAULT_HOST}
ENV PORT=${DEFAULT_PORT}
ENV MODEL_PATH=${DEFAULT_MODEL_PATH}
ENV MAX_NEW_TOKENS=${DEFAULT_MAX_NEW_TOKENS}

# Add option to pre-download model
ARG PREDOWNLOAD_MODEL=false
RUN if [ "$PREDOWNLOAD_MODEL" = "true" ]; then \
        python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; \
        model_id = '${MODEL_PATH}'; \
        print(f'Pre-downloading model: {model_id}'); \
        tokenizer = AutoTokenizer.from_pretrained(model_id); \
        model = AutoModelForCausalLM.from_pretrained(model_id)"; \
    fi

# Expose port
EXPOSE ${DEFAULT_PORT}

# Run the server
CMD ["python", "-m", "llm_agent"] 