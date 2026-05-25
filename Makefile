.PHONY: install redis-up redis-down api worker clean

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

install:
	@echo "Setting up virtual environment and installing dependencies..."
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

redis-up:
	@echo "Starting Redis infrastructure..."
	docker-compose up -d

redis-down:
	@echo "Stopping Redis infrastructure..."
	docker-compose down

api:
	@echo "Starting FastAPI Server..."
	$(VENV)/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	@echo "Starting Celery Worker..."
	$(VENV)/bin/celery -A app.celery_app worker --loglevel=info -Q xai-queue

clean:
	@echo "Cleaning up cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
