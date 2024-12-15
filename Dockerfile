# Stage 1: Build stage
FROM python:3.11-slim AS builder
WORKDIR /app

# Install build dependencies in a single layer to reduce image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    pip install -U setuptools wheel pip poetry==1.8.3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Configure poetry and export requirements
RUN poetry config virtualenvs.create false && \
    poetry export -f requirements.txt --output requirements.txt --without-hashes

# Install dependencies to site-packages
RUN pip install -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.11-slim
# Create non-root user
RUN useradd -m -u 1000 botuser

WORKDIR /app

# Install any runtime dependencies in a single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # Add any runtime dependencies your application needs here \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # Create necessary directories and set permissions in the same layer
    && mkdir -p /app/data \
    && chown -R botuser:botuser /app

# Copy only necessary files from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Copy application files
COPY main.py settings.py ./
# Ensure copied files have correct ownership
RUN chown -R botuser:botuser /app

# Switch to non-root user
USER botuser

# Command to run the bot directly with Python
CMD ["python", "main.py"]
