# OCR API

A Python OCR microservice built with FastAPI and PaddleOCR.

The API can extract text from:

- Scanned PDF documents
- Images (PNG, JPG, JPEG, TIFF, BMP, WEBP)

## Prerequisites

- Python 3.11
- UV
- Git
- Poppler, required only for PDF uploads

Install UV:

```bash
# Ubuntu / Debian
sudo apt install pipx
pipx install uv

# macOS
brew install uv
```

Verify your Python installation:

```bash
python3 --version
```

Install Poppler:

```bash
# Ubuntu / Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler
```

## Create a Virtual Environment

```bash
uv venv --python 3.11
```

Activate it:

```bash
source .venv/bin/activate
```

## Install Dependencies

```bash
uv pip install -r requirements.txt
```

Install test dependencies:

```bash
uv pip install -r requirements-test.txt
```

## Run the Application

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

## Project Structure

```text
ocr-api/
├── app/
│   ├── __init__.py
│   ├── dependencies.py
│   ├── domain/
│   │   └── ocr.py
│   ├── infrastructure/
│   │   └── paddle_ocr_engine.py
│   ├── main.py
│   └── services/
│       └── ocr_service.py
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md
```

## Architecture

The project separates API routing, application logic, OCR contracts, and the concrete OCR engine.

- `app/main.py` exposes the FastAPI routes.
- `app/dependencies.py` wires dependencies used by the API.
- `app/domain/ocr.py` defines the OCR interface and response types.
- `app/services/ocr_service.py` handles application logic, PDF conversion, and page orchestration.
- `app/infrastructure/paddle_ocr_engine.py` contains the PaddleOCR implementation.

## Test the API

```bash
curl -X POST \
  -F "file=@resume.pdf" \
  http://localhost:8000/ocr
```

Health check:

```bash
curl http://localhost:8000/health
```

## Docker

```bash
make docker-build
make docker-run
```

Override the image name or tag:

```bash
make docker-build IMAGE_NAME=ocr-api IMAGE_TAG=dev
```

## Development

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Deactivate:

```bash
deactivate
```

Run tests:

```bash
uv run pytest tests
```

Run tests with coverage:

```bash
uv run pytest --cov=app --cov-report=term-missing tests
```

Useful Make commands:

```bash
make venv
make install
make install-test
make dev
make test
make coverage
make docker-build
make docker-run
```
