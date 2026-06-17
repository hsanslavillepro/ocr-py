from functools import lru_cache
from pathlib import Path

from PIL import Image

from app.config import get_paddle_ocr_settings
from app.domain.ocr import OcrLine, OcrPage


class PaddleOcrEngine:
    def load_models(self) -> None:
        get_paddle_ocr()

    def recognize_image(self, image_path: Path, page_number: int) -> OcrPage:
        self._normalize_image(image_path)
        settings = get_paddle_ocr_settings()
        raw_result = get_paddle_ocr().ocr(str(image_path), cls=settings.use_angle_cls)

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

    settings = get_paddle_ocr_settings()
    # Loads the PaddleOCR models once per process; use_angle_cls improves rotated text handling.
    return PaddleOCR(
        use_angle_cls=settings.use_angle_cls,
        lang=settings.language,
        show_log=settings.show_log,
        ocr_version=settings.ocr_version,
        det_model_dir=settings.det_model_dir,
        rec_model_dir=settings.rec_model_dir,
        cls_model_dir=settings.cls_model_dir,
    )
