from functools import lru_cache
from pathlib import Path

from PIL import Image

from app.domain.ocr import OcrLine, OcrPage


class PaddleOcrEngine:
    def recognize_image(self, image_path: Path, page_number: int) -> OcrPage:
        self._normalize_image(image_path)
        raw_result = get_paddle_ocr().ocr(str(image_path), cls=True)

        lines: list[OcrLine] = []
        page_result = raw_result[0] if raw_result else []
        for entry in page_result or []:
            text, confidence = entry[1]
            lines.append({"text": text, "confidence": float(confidence)})

        return {
            "page": page_number,
            "text": "\n".join(line["text"] for line in lines),
            "lines": lines,
        }

    def _normalize_image(self, image_path: Path) -> None:
        with Image.open(image_path) as image:
            if image.mode not in {"RGB", "L"}:
                image.convert("RGB").save(image_path)


@lru_cache(maxsize=1)
def get_paddle_ocr():
    from paddleocr import PaddleOCR

    return PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
