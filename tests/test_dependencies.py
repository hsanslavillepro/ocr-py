from app.dependencies import get_ocr_service
from app.infrastructure.paddle_ocr_engine import PaddleOcrEngine
from app.services.ocr_service import OcrService


def test_get_ocr_service_returns_cached_service() -> None:
    get_ocr_service.cache_clear()

    first_service = get_ocr_service()
    second_service = get_ocr_service()

    assert first_service is second_service
    assert isinstance(first_service, OcrService)
    assert isinstance(first_service.engine, PaddleOcrEngine)

    get_ocr_service.cache_clear()
