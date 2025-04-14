FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy requirements first to leverage Docker cache
COPY pyproject.toml .
RUN uv pip install --no-cache --system .

# Copy source code
COPY server/ .

# Expose the port the app runs on
EXPOSE 3000

# Command to run the application
CMD ["mcp","run", "mcp_server.py"]