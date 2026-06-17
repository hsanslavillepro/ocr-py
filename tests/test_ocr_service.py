from pathlib import Path
from unittest.mock import Mock

import pytest

from app.services.ocr_service import OcrService


def test_run_recognizes_single_image() -> None:
    engine = Mock()
    engine.recognize_image.return_value = {
        "page": 1,
        "text": "Image text",
        "lines": [{"text": "Image text", "confidence": 0.99}],
    }
    service = OcrService(engine=engine)

    result = service.run(Path("sample.png"))

    assert result == {
        "text": "Image text",
        "pages": [
            {
                "page": 1,
                "text": "Image text",
                "lines": [{"text": "Image text", "confidence": 0.99}],
            }
        ],
    }
    engine.recognize_image.assert_called_once_with(Path("sample.png"), 1)


def test_run_converts_pdf_and_recognizes_each_page(monkeypatch) -> None:
    engine = Mock()
    engine.recognize_image.side_effect = [
        {"page": 1, "text": "Page one", "lines": []},
        {"page": 2, "text": "Page two", "lines": []},
    ]
    service = OcrService(engine=engine)

    image_paths = [Path("/tmp/page-1.png"), Path("/tmp/page-2.png")]
    monkeypatch.setattr(service, "_pdf_to_images", Mock(return_value=image_paths))

    result = service.run(Path("document.pdf"))

    assert result == {
        "text": "Page one\n\nPage two",
        "pages": [
            {"page": 1, "text": "Page one", "lines": []},
            {"page": 2, "text": "Page two", "lines": []},
        ],
    }
    assert engine.recognize_image.call_args_list[0].args == (image_paths[0], 1)
    assert engine.recognize_image.call_args_list[1].args == (image_paths[1], 2)


def test_pdf_to_images_saves_one_png_per_page(monkeypatch, tmp_path) -> None:
    first_page = Mock()
    second_page = Mock()
    monkeypatch.setattr(
        "app.services.ocr_service.convert_from_path",
        Mock(return_value=[first_page, second_page]),
    )
    service = OcrService(engine=Mock())

    result = service._pdf_to_images(Path("document.pdf"), tmp_path)

    assert result == [tmp_path / "page-1.png", tmp_path / "page-2.png"]
    first_page.save.assert_called_once_with(tmp_path / "page-1.png", "PNG")
    second_page.save.assert_called_once_with(tmp_path / "page-2.png", "PNG")


def test_pdf_to_images_raises_runtime_error_when_conversion_fails(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        "app.services.ocr_service.convert_from_path",
        Mock(side_effect=Exception("poppler missing")),
    )
    service = OcrService(engine=Mock())

    with pytest.raises(RuntimeError, match="Could not convert PDF to images"):
        service._pdf_to_images(Path("document.pdf"), tmp_path)
