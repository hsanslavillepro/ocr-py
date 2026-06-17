from app.config import (
    LoggingSettings,
    PaddleOcrSettings,
    get_logging_settings,
    get_paddle_ocr_settings,
)


def test_get_paddle_ocr_settings_returns_defaults(monkeypatch) -> None:
    monkeypatch.delenv("OCR_LANGUAGE", raising=False)
    monkeypatch.delenv("OCR_SHOW_LOG", raising=False)
    monkeypatch.delenv("OCR_USE_ANGLE_CLS", raising=False)
    monkeypatch.delenv("OCR_VERSION", raising=False)
    monkeypatch.delenv("OCR_DET_MODEL_DIR", raising=False)
    monkeypatch.delenv("OCR_REC_MODEL_DIR", raising=False)
    monkeypatch.delenv("OCR_CLS_MODEL_DIR", raising=False)
    get_paddle_ocr_settings.cache_clear()

    settings = get_paddle_ocr_settings()

    assert settings == PaddleOcrSettings(
        language="en",
        show_log=False,
        use_angle_cls=True,
        ocr_version="PP-OCRv4",
        det_model_dir="models/paddleocr/det",
        rec_model_dir="models/paddleocr/rec",
        cls_model_dir="models/paddleocr/cls",
    )

    get_paddle_ocr_settings.cache_clear()


def test_get_paddle_ocr_settings_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("OCR_LANGUAGE", "fr")
    monkeypatch.setenv("OCR_SHOW_LOG", "true")
    monkeypatch.setenv("OCR_USE_ANGLE_CLS", "false")
    monkeypatch.setenv("OCR_VERSION", "PP-OCRv3")
    monkeypatch.setenv("OCR_DET_MODEL_DIR", "/models/det")
    monkeypatch.setenv("OCR_REC_MODEL_DIR", "/models/rec")
    monkeypatch.setenv("OCR_CLS_MODEL_DIR", "/models/cls")
    get_paddle_ocr_settings.cache_clear()

    settings = get_paddle_ocr_settings()

    assert settings == PaddleOcrSettings(
        language="fr",
        show_log=True,
        use_angle_cls=False,
        ocr_version="PP-OCRv3",
        det_model_dir="/models/det",
        rec_model_dir="/models/rec",
        cls_model_dir="/models/cls",
    )

    get_paddle_ocr_settings.cache_clear()


def test_get_logging_settings_returns_default(monkeypatch) -> None:
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    get_logging_settings.cache_clear()

    settings = get_logging_settings()

    assert settings == LoggingSettings(level="INFO")

    get_logging_settings.cache_clear()


def test_get_logging_settings_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "debug")
    get_logging_settings.cache_clear()

    settings = get_logging_settings()

    assert settings == LoggingSettings(level="DEBUG")

    get_logging_settings.cache_clear()
