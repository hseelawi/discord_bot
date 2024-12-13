# Stage 1: Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Update dependencies
RUN apt update
RUN pip install -U setuptools wheel pip

# Install build dependencies
RUN pip install poetry==1.8.3

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

# Create necessary directories
RUN mkdir -p /app/data && \
    chown -R botuser:botuser /app

# Copy only necessary files from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Copy application files
COPY prompt.txt main.py settings.py ./

# Switch to non-root user
USER botuser

# Command to run the bot directly with Python
CMD ["python", "main.py"]
