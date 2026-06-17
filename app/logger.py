import logging
import sys

from app.config import get_logging_settings


def configure_logging() -> None:
    settings = get_logging_settings()
    logging.basicConfig(
        level=settings.level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        stream=sys.stdout,
        force=True,
    )
    logging.getLogger("app").setLevel(settings.level)
