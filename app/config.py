import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class PaddleOcrSettings:
    language: str = "en"
    show_log: bool = False
    use_angle_cls: bool = True
    ocr_version: str = "PP-OCRv4"
    det_model_dir: str = "models/paddleocr/det"
    rec_model_dir: str = "models/paddleocr/rec"
    cls_model_dir: str = "models/paddleocr/cls"


@dataclass(frozen=True)
class LoggingSettings:
    level: str = "INFO"


@lru_cache(maxsize=1)
def get_paddle_ocr_settings() -> PaddleOcrSettings:
    return PaddleOcrSettings(
        language=os.getenv("OCR_LANGUAGE", PaddleOcrSettings.language),
        show_log=_env_bool("OCR_SHOW_LOG", PaddleOcrSettings.show_log),
        use_angle_cls=_env_bool("OCR_USE_ANGLE_CLS", PaddleOcrSettings.use_angle_cls),
        ocr_version=os.getenv("OCR_VERSION", PaddleOcrSettings.ocr_version),
        det_model_dir=os.getenv("OCR_DET_MODEL_DIR", PaddleOcrSettings.det_model_dir),
        rec_model_dir=os.getenv("OCR_REC_MODEL_DIR", PaddleOcrSettings.rec_model_dir),
        cls_model_dir=os.getenv("OCR_CLS_MODEL_DIR", PaddleOcrSettings.cls_model_dir),
    )


@lru_cache(maxsize=1)
def get_logging_settings() -> LoggingSettings:
    return LoggingSettings(level=os.getenv("LOG_LEVEL", LoggingSettings.level).upper())


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}
