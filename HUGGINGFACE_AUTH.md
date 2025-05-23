# Using Hugging Face Authentication in LLM Tool Agent

## Problem
When trying to use Hugging Face models that require authentication (like Mistral, Llama, etc.), you might see errors like:

```
Failed to load model 'mistralai/Mistral-7B-Instruct-v0.2': You are trying to access a gated repo
```

## Solution

1. **Get a Hugging Face token**:
   - Create an account at https://huggingface.co
   - Generate a token at https://huggingface.co/settings/tokens
   - Request access to the model you want to use (e.g., visit the model page and click "Access repository")

2. **Rebuild the Docker image**:
   ```bash
   # Force a rebuild of the image with updated dependencies
   REBUILD=true HUGGINGFACE_TOKEN=your_token_here ./run_docker.sh
   ```

3. **Alternative: Run manually**:
   ```bash
   # Build the image
   docker build -t llm-agent .

   # Run with your token
   docker run --gpus all \
     -e HUGGINGFACE_TOKEN=your_token_here \
     -e MODEL_PATH=mistralai/Mistral-7B-Instruct-v0.2 \
     -p 8000:8000 \
     -v $(pwd)/data:/app/data \
     -v huggingface-cache:/root/.cache/huggingface \
     llm-agent
   ```

## Dependency Conflicts

If you're experiencing dependency conflicts with vllm and transformers, try building without vllm:

```bash
# Build without vllm (simplified dependencies)
REBUILD=true USE_VLLM=false HUGGINGFACE_TOKEN=your_token_here ./run_docker.sh
```

## Using Open Models

If you don't want to deal with authentication, use an open model instead:

```bash
MODEL_PATH=microsoft/phi-2 ./run_docker.sh
```

## How the Fix Works

1. We set compatible versions of `transformers`, `tokenizers`, and `huggingface-hub` in requirements.txt
2. We create a `/root/.huggingface/token` file with your token
3. The model initialization code uses this token to authenticate with the Hugging Face API

## Troubleshooting

If you still see errors:

1. Make sure your token has access to the model you're trying to use
2. Try using the REBUILD=true flag to force a complete rebuild of the image
3. If you receive tokenization errors, try a different model or build without vllm (USE_VLLM=false)
4. Check your GPU memory - some models require significant VRAM