FROM ghcr.io/astral-sh/uv:debian-slim

ENV OLLAMA_HOST=http://ollama:11434
ENV OLLAMA_MODEL=llama3.2:3b
ENV OLLAMA_EMBED_MODEL=mxbai-embed-large
ENV OLLAMA_MODEL_TEMPERATURE=0
ENV CHROMA_HOST=http://chroma:8000
ENV MD_REPO=/app/md-repo

ADD . /app

WORKDIR /app

RUN uv sync --locked

CMD ["uv", "run", "main.py"]
