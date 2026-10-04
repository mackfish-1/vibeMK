# vibeMK as a central MCP server over Streamable HTTP.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install . && useradd --system --no-create-home vibemk

USER vibemk

# Inside the container vibeMK must listen on all interfaces to be reachable;
# docker-compose.yml decides what the host actually exposes.
ENV VIBEMK_TRANSPORT=http \
    VIBEMK_HTTP_HOST=0.0.0.0 \
    VIBEMK_HTTP_PORT=8765 \
    VIBEMK_HTTP_PATH=/mcp

EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os, socket; socket.create_connection(('127.0.0.1', int(os.environ['VIBEMK_HTTP_PORT'])), 3)"

ENTRYPOINT ["vibemk"]
