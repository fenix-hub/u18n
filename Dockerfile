FROM python:3.13.3-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    pkg-config \
    cmake \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn depencendy
RUN pip install --no-cache-dir gunicorn

# Copy application code
COPY . .

# Environment variables
ENV FLASK_APP=app/main.py
ENV FLASK_ENV=production
ENV PORT=5000

# Expose the port the app runs on
EXPOSE 5000

# Run the application using gunicorn for production
CMD ["gunicorn", "-c", "config/gunicorn_config.py", "app.main:app"]