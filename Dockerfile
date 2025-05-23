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
COPY requirements*.txt /app/

# Set build arg for choosing requirements file
ARG USE_VLLM=true
RUN if [ "$USE_VLLM" = "true" ]; then \
    pip install --no-cache-dir -r requirements.txt; \
    else \
    pip install --no-cache-dir -r requirements-simple.txt; \
    fi

# Create .cache directory for Hugging Face
RUN mkdir -p /root/.cache/huggingface

# Set up Hugging Face credentials
RUN echo 'function setup_hf_token() {\n\
    if [ -n "$HUGGINGFACE_TOKEN" ]; then\n\
        mkdir -p /root/.huggingface\n\
        echo -n "$HUGGINGFACE_TOKEN" > /root/.huggingface/token\n\
        echo "Hugging Face token configured"\n\
    else\n\
        echo "WARNING: HUGGINGFACE_TOKEN not set"\n\
    fi\n\
}\n\
setup_hf_token\n\
exec "$@"' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Copy the rest of the code
COPY . /app/

# Set environment variables with defaults (can be overridden at runtime)
ENV HOST=0.0.0.0
ENV PORT=8000
ENV MODEL_PATH=mistralai/Mistral-7B-Instruct-v0.2
ENV MAX_NEW_TOKENS=1024

# Expose port
EXPOSE 8000

# Set entrypoint to handle token setup
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]

# Run the server
CMD ["python", "-m", "llm_agent"]