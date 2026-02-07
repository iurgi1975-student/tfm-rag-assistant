# Use Python 3.13 slim image as base (better compatibility than Alpine)
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Upgrade pip to ensure we can use prebuilt wheels when available
RUN pip install --upgrade pip

# Install PyTorch CPU-only version (much smaller, no CUDA)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create necessary directories for data persistence
RUN mkdir -p /app/chroma_db /app/data /app/logs

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Volumes for data persistence
VOLUME ["/app/chroma_db", "/app/data"]

# Expose the port (Railway will provide the PORT env var)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:${PORT:-7860}/ || exit 1

# Default command to run the application (uses Ollama by default)
CMD ["python", "app.py", "--host", "0.0.0.0"]
