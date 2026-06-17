PYTHON_VERSION ?= 3.11
HOST ?= 0.0.0.0
PORT ?= 8000
IMAGE_NAME ?= ocr-api
IMAGE_TAG ?= latest

.PHONY: venv install install-test run dev test coverage docker-build docker-run clean

venv:
	uv venv --python $(PYTHON_VERSION)

install:
	uv pip install -r requirements.txt

install-test:
	uv pip install -r requirements-test.txt

run:
	uv run uvicorn app.main:app --host $(HOST) --port $(PORT)

dev:
	uv run uvicorn app.main:app --reload --host $(HOST) --port $(PORT)

test:
	uv run pytest tests

coverage:
	uv run pytest --cov=app --cov-report=term-missing tests

docker-build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

docker-run:
	docker run --rm -p $(PORT):8000 $(IMAGE_NAME):$(IMAGE_TAG)

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
