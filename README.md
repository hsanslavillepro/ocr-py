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
│   ├── config.py
│   ├── dependencies.py
│   ├── logger.py
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

- `app/config.py` reads PaddleOCR configuration from environment variables.
- `app/logger.py` configures application logging.
- `app/main.py` exposes the FastAPI routes.
- `app/dependencies.py` wires dependencies used by the API.
- `app/domain/ocr.py` defines the OCR interface and response types.
- `app/services/ocr_service.py` handles application logic, PDF conversion, and page orchestration.
- `app/infrastructure/paddle_ocr_engine.py` contains the PaddleOCR implementation.

## Configuration

PaddleOCR options can be configured with environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `LOG_LEVEL` | `INFO` | Application log level: `DEBUG`, `INFO`, or `ERROR`. |
| `OCR_LANGUAGE` | `en` | OCR language model used by PaddleOCR. |
| `OCR_SHOW_LOG` | `false` | Enables PaddleOCR logs when set to `true`. |
| `OCR_USE_ANGLE_CLS` | `true` | Enables angle classification for rotated text. |
| `OCR_VERSION` | `PP-OCRv4` | PaddleOCR model family. |
| `OCR_DET_MODEL_DIR` | `models/paddleocr/det` | Local text detection model directory. |
| `OCR_REC_MODEL_DIR` | `models/paddleocr/rec` | Local text recognition model directory. |
| `OCR_CLS_MODEL_DIR` | `models/paddleocr/cls` | Local angle classifier model directory. |

Example:

```bash
LOG_LEVEL=DEBUG OCR_LANGUAGE=fr OCR_SHOW_LOG=true OCR_USE_ANGLE_CLS=false make dev
```

PaddleOCR will use the configured model directories. If a directory does not contain
`inference.pdmodel` and `inference.pdiparams`, PaddleOCR downloads the matching model
there on first use. The default `models/` folder is ignored by git.

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

Readiness check:

```bash
curl http://localhost:8000/ready
```

`/health` only checks that the API process is running. `/ready` loads the OCR
service and PaddleOCR models, returning `503` if the models cannot be initialized.

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

Override OCR configuration:

```bash
make dev LOG_LEVEL=DEBUG OCR_LANGUAGE=fr OCR_SHOW_LOG=true OCR_USE_ANGLE_CLS=false
```
