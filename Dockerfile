# Dockerfile for Pramiti AI Organization Platform
# Production-ready containerized deployment

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies (including ChromaDB for RAG)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir chromadb gunicorn

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 pramiti && \
    chown -R pramiti:pramiti /app && \
    mkdir -p /app/data/rag/chroma /app/data/rag/conversations /app/logs /app/secrets && \
    chown -R pramiti:pramiti /app/data /app/logs /app/secrets

# Switch to non-root user
USER pramiti

# Expose port
EXPOSE 8084

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8084/health || exit 1

# Start application
CMD ["python3", "-m", "uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8084", "--workers", "4"]
