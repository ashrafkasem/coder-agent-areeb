# Simple Docker usage for LLM Tool Agent

## Build the image

```
docker build -t llm-agent .
```

## Run the container (with GPU, Hugging Face token, and custom settings)

```
docker run --gpus all \
  -e HUGGINGFACE_TOKEN=your_hf_token_here \
  -e MODEL_PATH=mistralai/Mistral-7B-Instruct-v0.2 \
  -e MAX_NEW_TOKENS=1024 \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v huggingface-cache:/root/.cache/huggingface \
  llm-agent
```

- Replace `your_hf_token_here` with your Hugging Face token.
- You can add `-e INITIAL_API_KEY=your_api_key` if you want a fixed API key.
- The `data` directory and Hugging Face cache will persist on your host.
- The server will be available at `http://localhost:8000`.

## Remove old files
- You can now delete `docker-compose.yml` and `Makefile` if you wish.

---

**This is all you need for simple Docker-based deployment!**
