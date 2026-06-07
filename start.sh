#!/bin/sh

# Start Celery worker in background
celery -A app.celery_app worker --loglevel=info -Q xai-queue &

# Start FastAPI app in foreground
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
