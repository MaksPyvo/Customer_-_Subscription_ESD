FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/app

# Install system deps needed to build psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
 && rm -rf /var/lib/apt/lists/*

# Copy and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port the app listens on
EXPOSE 7500

# Run the app
CMD ["python", "-m", "app.app"]