# Use Python 3.13 slim image as base
FROM python:3.13-alpine

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apk update && apk add --no-cache \
    build-base \
    wget \
    rust \
    cargo

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Upgrade pip to ensure we can use prebuilt wheels when available
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/documents /app/vectorstore /app/logs

# Create a non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose the port (Railway will provide the PORT env var)
EXPOSE 7860

# Health check - use wget instead of curl as it's more likely to be available
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:${PORT:-7860}/ || exit 1

# Default command to run the application
# Railway will provide the PORT environment variable
CMD ["python", "app.py", "--host", "0.0.0.0"]
