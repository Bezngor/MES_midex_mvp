FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Copy application code (maintain backend/src structure)
COPY src/ ./backend/src/

# Set PYTHONPATH to make imports work
ENV PYTHONPATH=/app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "backend.src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
