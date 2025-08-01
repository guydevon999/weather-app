FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    sqlite3 && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files (including data directory)
COPY . .

# Create database (will be created with proper permissions)
# RUN python app/create_db.py

ENV PYTHONPATH=/app

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
