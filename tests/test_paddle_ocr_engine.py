from pathlib import Path
from unittest.mock import MagicMock, Mock

from app.config import PaddleOcrSettings
from app.infrastructure.paddle_ocr_engine import PaddleOcrEngine


def test_load_models_initializes_paddle_ocr(monkeypatch) -> None:
    get_paddle_ocr = Mock()
    monkeypatch.setattr("app.infrastructure.paddle_ocr_engine.get_paddle_ocr", get_paddle_ocr)

    PaddleOcrEngine().load_models()

    get_paddle_ocr.assert_called_once()


def test_recognize_image_parses_paddle_result(monkeypatch) -> None:
    paddle_ocr = Mock()
    paddle_ocr.ocr.return_value = [
        [
            [None, ("First line", 0.97)],
            [None, ("Second line", 0.88)],
        ]
    ]
    monkeypatch.setattr(
        "app.infrastructure.paddle_ocr_engine.get_paddle_ocr",
        Mock(return_value=paddle_ocr),
    )
    monkeypatch.setattr(
        "app.infrastructure.paddle_ocr_engine.get_paddle_ocr_settings",
        Mock(return_value=PaddleOcrSettings(use_angle_cls=True)),
    )
    monkeypatch.setattr(PaddleOcrEngine, "_normalize_image", Mock())

    result = PaddleOcrEngine().recognize_image(Path("sample.png"), 3)

    assert result == {
        "page": 3,
        "text": "First line\nSecond line",
        "lines": [
            {"text": "First line", "confidence": 0.97},
            {"text": "Second line", "confidence": 0.88},
        ],
    }
    paddle_ocr.ocr.assert_called_once_with("sample.png", cls=True)


def test_recognize_image_uses_angle_classifier_setting(monkeypatch) -> None:
    paddle_ocr = Mock()
    paddle_ocr.ocr.return_value = []
    monkeypatch.setattr(
        "app.infrastructure.paddle_ocr_engine.get_paddle_ocr",
        Mock(return_value=paddle_ocr),
    )
    monkeypatch.setattr(
        "app.infrastructure.paddle_ocr_engine.get_paddle_ocr_settings",
        Mock(return_value=PaddleOcrSettings(use_angle_cls=False)),
    )
    monkeypatch.setattr(PaddleOcrEngine, "_normalize_image", Mock())

    PaddleOcrEngine().recognize_image(Path("sample.png"), 1)

    paddle_ocr.ocr.assert_called_once_with("sample.png", cls=False)


def test_recognize_image_handles_empty_paddle_result(monkeypatch) -> None:
    paddle_ocr = Mock()
    paddle_ocr.ocr.return_value = []
    monkeypatch.setattr(
        "app.infrastructure.paddle_ocr_engine.get_paddle_ocr",
        Mock(return_value=paddle_ocr),
    )
    monkeypatch.setattr(
        "app.infrastructure.paddle_ocr_engine.get_paddle_ocr_settings",
        Mock(return_value=PaddleOcrSettings()),
    )
    monkeypatch.setattr(PaddleOcrEngine, "_normalize_image", Mock())

    result = PaddleOcrEngine().recognize_image(Path("sample.png"), 1)

    assert result == {"page": 1, "text": "", "lines": []}


def test_get_paddle_ocr_uses_settings(monkeypatch) -> None:
    paddle_ocr_class = Mock()
    monkeypatch.setattr("paddleocr.PaddleOCR", paddle_ocr_class)
    monkeypatch.setattr(
        "app.infrastructure.paddle_ocr_engine.get_paddle_ocr_settings",
        Mock(return_value=PaddleOcrSettings(language="fr", show_log=True, use_angle_cls=False)),
    )

    from app.infrastructure.paddle_ocr_engine import get_paddle_ocr

    get_paddle_ocr.cache_clear()
    get_paddle_ocr()

    paddle_ocr_class.assert_called_once_with(
        use_angle_cls=False,
        lang="fr",
        show_log=True,
        ocr_version="PP-OCRv4",
        det_model_dir="models/paddleocr/det",
        rec_model_dir="models/paddleocr/rec",
        cls_model_dir="models/paddleocr/cls",
    )
    get_paddle_ocr.cache_clear()


def test_normalize_image_converts_non_rgb_images(monkeypatch) -> None:
    image = Mock()
    image.mode = "RGBA"
    converted = Mock()
    image.convert.return_value = converted
    image_context = MagicMock()
    image_context.__enter__.return_value = image
    image_context.__exit__.return_value = None
    image_open = Mock(return_value=image_context)
    monkeypatch.setattr("app.infrastructure.paddle_ocr_engine.Image.open", image_open)

    PaddleOcrEngine()._normalize_image(Path("sample.png"))

    image_open.assert_called_once_with(Path("sample.png"))
    image.convert.assert_called_once_with("RGB")
    converted.save.assert_called_once_with(Path("sample.png"))


def test_normalize_image_leaves_rgb_images_unchanged(monkeypatch) -> None:
    image = Mock()
    image.mode = "RGB"
    image_context = MagicMock()
    image_context.__enter__.return_value = image
    image_context.__exit__.return_value = None
    image_open = Mock(return_value=image_context)
    monkeypatch.setattr("app.infrastructure.paddle_ocr_engine.Image.open", image_open)

    PaddleOcrEngine()._normalize_image(Path("sample.png"))

    image.convert.assert_not_called()
