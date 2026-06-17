from pathlib import Path
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

# Health endpoint for kubernetes
def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# Validate Success call for OCR returns 200
def test_extract_text_uses_ocr_service(monkeypatch) -> None:
    ocr_result = {
        "text": "Hello OCR",
        "pages": [
            {
                "page": 1,
                "text": "Hello OCR",
                "lines": [{"text": "Hello OCR", "confidence": 0.98}],
            }
        ],
    }
    service = Mock()
    service.run.return_value = ocr_result
    monkeypatch.setattr("app.main.get_ocr_service", Mock(return_value=service))

    response = client.post(
        "/ocr",
        files={"file": ("sample.png", b"image-content", "image/png")},
    )

    assert response.status_code == 200
    assert response.json() == ocr_result
    service.run.assert_called_once()
    input_path = service.run.call_args.args[0]
    assert isinstance(input_path, Path)
    assert input_path.suffix == ".png"

# Validate response code 400 due to unsupported file type
def test_extract_text_rejects_unsupported_file_type(monkeypatch) -> None:
    get_ocr_service = Mock()
    monkeypatch.setattr("app.main.get_ocr_service", get_ocr_service)

    response = client.post(
        "/ocr",
        files={"file": ("sample.txt", b"plain text", "text/plain")},
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
    get_ocr_service.assert_not_called()

# Validate response code 400 due to empty file
def test_extract_text_rejects_empty_file(monkeypatch) -> None:
    get_ocr_service = Mock()
    monkeypatch.setattr("app.main.get_ocr_service", get_ocr_service)

    response = client.post(
        "/ocr",
        files={"file": ("sample.png", b"", "image/png")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Uploaded file is empty."}
    get_ocr_service.assert_not_called()

# Validate response code 500 due to ocr failure
def test_extract_text_returns_500_when_service_fails(monkeypatch) -> None:
    service = Mock()
    service.run.side_effect = RuntimeError("OCR failed")
    monkeypatch.setattr("app.main.get_ocr_service", Mock(return_value=service))

    response = client.post(
        "/ocr",
        files={"file": ("sample.png", b"image-content", "image/png")},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "OCR failed"}
