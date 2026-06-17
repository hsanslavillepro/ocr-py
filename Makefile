PYTHON_VERSION ?= 3.11
HOST ?= 0.0.0.0
PORT ?= 8000
IMAGE_NAME ?= ocr-api
IMAGE_TAG ?= latest
OCR_LANGUAGE ?= fr
OCR_SHOW_LOG ?= false
OCR_USE_ANGLE_CLS ?= true
OCR_VERSION ?= PP-OCRv4
OCR_DET_MODEL_DIR ?= models/paddleocr/det
OCR_REC_MODEL_DIR ?= models/paddleocr/rec
OCR_CLS_MODEL_DIR ?= models/paddleocr/cls
LOG_LEVEL ?= INFO

.PHONY: venv install install-test run dev test coverage docker-build docker-run clean

venv:
	uv venv --python $(PYTHON_VERSION)

install:
	uv pip install -r requirements.txt

install-test:
	uv pip install -r requirements-test.txt

run:
	LOG_LEVEL=$(LOG_LEVEL) OCR_LANGUAGE=$(OCR_LANGUAGE) OCR_SHOW_LOG=$(OCR_SHOW_LOG) OCR_USE_ANGLE_CLS=$(OCR_USE_ANGLE_CLS) OCR_VERSION=$(OCR_VERSION) OCR_DET_MODEL_DIR=$(OCR_DET_MODEL_DIR) OCR_REC_MODEL_DIR=$(OCR_REC_MODEL_DIR) OCR_CLS_MODEL_DIR=$(OCR_CLS_MODEL_DIR) uv run uvicorn app.main:app --host $(HOST) --port $(PORT)

dev:
	LOG_LEVEL=$(LOG_LEVEL) OCR_LANGUAGE=$(OCR_LANGUAGE) OCR_SHOW_LOG=$(OCR_SHOW_LOG) OCR_USE_ANGLE_CLS=$(OCR_USE_ANGLE_CLS) OCR_VERSION=$(OCR_VERSION) OCR_DET_MODEL_DIR=$(OCR_DET_MODEL_DIR) OCR_REC_MODEL_DIR=$(OCR_REC_MODEL_DIR) OCR_CLS_MODEL_DIR=$(OCR_CLS_MODEL_DIR) uv run uvicorn app.main:app --reload --host $(HOST) --port $(PORT)

test:
	uv run pytest tests

coverage: install-test
	uv run pytest --cov=app --cov-report=term-missing tests

docker-build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

docker-run:
	docker run --rm -p $(PORT):8000 -e LOG_LEVEL=$(LOG_LEVEL) -e OCR_LANGUAGE=$(OCR_LANGUAGE) -e OCR_SHOW_LOG=$(OCR_SHOW_LOG) -e OCR_USE_ANGLE_CLS=$(OCR_USE_ANGLE_CLS) -e OCR_VERSION=$(OCR_VERSION) -e OCR_DET_MODEL_DIR=$(OCR_DET_MODEL_DIR) -e OCR_REC_MODEL_DIR=$(OCR_REC_MODEL_DIR) -e OCR_CLS_MODEL_DIR=$(OCR_CLS_MODEL_DIR) $(IMAGE_NAME):$(IMAGE_TAG)

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
