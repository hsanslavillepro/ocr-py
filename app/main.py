import logging
from time import perf_counter
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from starlette.concurrency import run_in_threadpool

from app.dependencies import get_ocr_service
from app.domain.ocr import OcrResult
from app.logger import configure_logging


configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="OCR API",
    description="Extract text from image and PDF files using PaddleOCR.",
    version="0.1.0",
)

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict[str, str]:
    started_at = perf_counter()
    try:
        await run_in_threadpool(get_ocr_service().ensure_ready)
    except Exception as exc:
        elapsed_ms = (perf_counter() - started_at) * 1000
        logger.error("OCR readiness failed duration_ms=%.2f error=%s", elapsed_ms, exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OCR models are not ready.",
        ) from exc

    elapsed_ms = (perf_counter() - started_at) * 1000
    logger.info("OCR readiness completed duration_ms=%.2f", elapsed_ms)
    return {"status": "ready"}


@app.post("/ocr")
async def extract_text(file: Annotated[UploadFile, File(...)]) -> OcrResult:
    started_at = perf_counter()
    filename = file.filename or ""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        supported = ", ".join(sorted(ALLOWED_EXTENSIONS))
        logger.error("Rejected unsupported OCR upload filename=%s file_type=%s", filename, suffix or "unknown")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported extensions: {supported}",
        )

    contents = await file.read()
    file_size = len(contents)
    if not contents:
        logger.error("Rejected empty OCR upload filename=%s file_type=%s file_size=%s", filename, suffix, file_size)
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    logger.debug("Accepted OCR upload filename=%s file_type=%s file_size=%s", filename, suffix, file_size)

    with TemporaryDirectory() as tmp_dir:
        input_path = Path(tmp_dir) / f"upload{suffix}"
        input_path.write_bytes(contents)

        try:
            result = await run_in_threadpool(get_ocr_service().run, input_path)
        except RuntimeError as exc:
            elapsed_ms = (perf_counter() - started_at) * 1000
            logger.error(
                "OCR processing failed filename=%s file_type=%s file_size=%s duration_ms=%.2f error=%s",
                filename,
                suffix,
                file_size,
                elapsed_ms,
                exc,
            )
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    elapsed_ms = (perf_counter() - started_at) * 1000
    logger.info(
        "OCR processing completed filename=%s file_type=%s file_size=%s duration_ms=%.2f",
        filename,
        suffix,
        file_size,
        elapsed_ms,
    )
    return result
