from functools import lru_cache

from app.infrastructure.paddle_ocr_engine import PaddleOcrEngine
from app.services.ocr_service import OcrService


@lru_cache(maxsize=1)
def get_ocr_service() -> OcrService:
    return OcrService(engine=PaddleOcrEngine())
