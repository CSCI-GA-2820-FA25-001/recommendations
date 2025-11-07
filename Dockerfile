# Production container image for the Recommendations service
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies using Pipenv lockfile
COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir --upgrade pip pipenv \
    && pipenv install --system --deploy

# Copy application code
COPY . /app

# Service configuration
ENV PORT=8080
EXPOSE 8080

# Start the service with Gunicorn (use shell form so ${PORT} expands)
CMD sh -lc 'gunicorn --bind 0.0.0.0:${PORT} --log-level=info wsgi:app'
