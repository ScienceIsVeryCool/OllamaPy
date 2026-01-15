FROM python:3.14-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir flask flask-cors

# Copy application code
COPY src/ ./src/
COPY setup.py .
COPY README.md .
COPY LICENSE .

# Install the package
RUN pip install -e .

# Create non-root user first
RUN groupadd -r ollamapy && useradd -r -g ollamapy ollamapy --home-dir /home/ollamapy --create-home

# Create directory for user skills in user's home
RUN mkdir -p /home/ollamapy/.ollamapy/skills && \
    chown -R ollamapy:ollamapy /app /home/ollamapy/.ollamapy
VOLUME ["/home/ollamapy/.ollamapy/skills"]

# Switch to non-root user
USER ollamapy

# Set user home directory
ENV HOME=/home/ollamapy

# Expose port for skill editor
EXPOSE 8765

# Health check - using python instead of curl for non-root user
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8765', timeout=5)" || exit 1

# Default command - run skill editor
CMD ["python", "-m", "ollamapy", "--skill-editor", "--port", "8765"]

# Labels
LABEL maintainer="ScienceIsVeryCool" \
      description="OllamaPy - AI Chat Interface with Interactive Skill Editor" \
      version="0.8.0" \
      repository="https://github.com/ScienceIsVeryCool/OllamaPy"