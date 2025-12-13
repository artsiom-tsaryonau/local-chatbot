FROM ghcr.io/astral-sh/uv:debian-slim

# important for gradio running in docker
ENV GRADIO_SERVER_NAME="0.0.0.0"

ENV CHROMA_HOST=http://chroma:8000
ENV OLLAMA_HOST=http://ollama:11434
ENV OLLAMA_EMBED_MODEL=mxbai-embed-large
ENV OLLAMA_MODEL=llama3.2:3b

WORKDIR /usr/src/app
COPY . .

RUN uv sync --locked

EXPOSE 7860

CMD ["uv", "run", "main.py"]
