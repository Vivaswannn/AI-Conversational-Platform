FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY . .

# Make the entrypoint executable before switching to non-root user
RUN chmod +x /app/docker/entrypoint.sh

# Give ownership to app user
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# entrypoint.sh runs: alembic upgrade head → uvicorn
ENTRYPOINT ["/app/docker/entrypoint.sh"]
