from pathlib import Path
from typing import Protocol, TypedDict


class OcrLine(TypedDict):
    text: str
    confidence: float


class OcrPage(TypedDict):
    page: int
    text: str
    lines: list[OcrLine]


class OcrResult(TypedDict):
    text: str
    pages: list[OcrPage]


class OcrEngine(Protocol):
    def recognize_image(self, image_path: Path, page_number: int) -> OcrPage:
        """Extract OCR lines from one image file."""
