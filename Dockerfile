# Multi-stage build for minimal image size
FROM python:3.10-slim as builder

WORKDIR /app

# Install dependencies in builder stage
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.10-slim

WORKDIR /app

# Copy only necessary Python packages from builder
COPY --from=builder /root/.local /root/.local

# Set PATH to use pip installed packages
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Copy application code
COPY bot.py config.py ./
COPY handlers ./handlers
COPY services ./services
COPY database ./database
COPY keyboards ./keyboards
COPY utils ./utils

# Create data volume for database
VOLUME /app/data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sqlite3; sqlite3.connect('/app/data/bot_database.db')" || exit 1

# Run bot
CMD ["python", "bot.py"]
