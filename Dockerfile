FROM python:3.11-slim

WORKDIR /app

# Install system deps for chromadb
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies first (layer cache)
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

# Copy source code and knowledge base
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY knowledge_base/ ./knowledge_base/

# Railway uses $PORT; default 8000 for local Docker
ENV PORT=8000
EXPOSE ${PORT}

CMD uvicorn luxia_companion.main:app --host 0.0.0.0 --port $PORT
