FROM python:3.10-slim

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

# Create directory for user skills
RUN mkdir -p /root/.ollamapy/skills
VOLUME ["/root/.ollamapy/skills"]

# Create non-root user for security (optional)
RUN groupadd -r ollamapy && useradd -r -g ollamapy ollamapy
RUN chown -R ollamapy:ollamapy /app /root/.ollamapy
USER ollamapy

# Expose port for skill editor
EXPOSE 8765

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8765/ || exit 1

# Default command - run skill editor
CMD ["python", "-m", "ollamapy", "--skill-editor", "--port", "8765"]

# Labels
LABEL maintainer="ScienceIsVeryCool" \
      description="OllamaPy - AI Chat Interface with Interactive Skill Editor" \
      version="0.8.0" \
      repository="https://github.com/ScienceIsVeryCool/OllamaPy"