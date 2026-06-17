from pathlib import Path
from tempfile import TemporaryDirectory

from pdf2image import convert_from_path

from app.domain.ocr import OcrEngine, OcrResult


class OcrService:
    def __init__(self, engine: OcrEngine) -> None:
        self.engine = engine

    def ensure_ready(self) -> None:
        self.engine.load_models()

    def run(self, input_path: Path) -> OcrResult:
        if input_path.suffix.lower() == ".pdf":
            with TemporaryDirectory() as tmp_dir:
                image_paths = self._pdf_to_images(input_path, Path(tmp_dir))
                pages = [
                    self.engine.recognize_image(path, page_number)
                    for page_number, path in enumerate(image_paths, start=1)
                ]
        else:
            pages = [self.engine.recognize_image(input_path, 1)]

        return {
            "text": "\n\n".join(page["text"] for page in pages if page["text"]),
            "pages": pages,
        }

    def _pdf_to_images(self, input_path: Path, output_dir: Path) -> list[Path]:
        try:
            pages = convert_from_path(input_path, dpi=300)
        except Exception as exc:
            raise RuntimeError(
                "Could not convert PDF to images. Make sure Poppler is installed on the system."
            ) from exc

        image_paths = []
        for index, page in enumerate(pages, start=1):
            image_path = output_dir / f"page-{index}.png"
            page.save(image_path, "PNG")
            image_paths.append(image_path)

        return image_paths
