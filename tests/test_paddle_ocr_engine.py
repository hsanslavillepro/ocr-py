from pathlib import Path
from unittest.mock import MagicMock, Mock

from app.infrastructure.paddle_ocr_engine import PaddleOcrEngine


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


def test_recognize_image_handles_empty_paddle_result(monkeypatch) -> None:
    paddle_ocr = Mock()
    paddle_ocr.ocr.return_value = []
    monkeypatch.setattr(
        "app.infrastructure.paddle_ocr_engine.get_paddle_ocr",
        Mock(return_value=paddle_ocr),
    )
    monkeypatch.setattr(PaddleOcrEngine, "_normalize_image", Mock())

    result = PaddleOcrEngine().recognize_image(Path("sample.png"), 1)

    assert result == {"page": 1, "text": "", "lines": []}


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
