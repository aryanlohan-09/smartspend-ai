import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask


def configure_logging(app: Flask) -> None:
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
    app.logger.setLevel(log_level)

    if app.debug or app.testing:
        return

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    file_handler = RotatingFileHandler(
        log_dir / "smartspend.log",
        maxBytes=1_000_000,
        backupCount=3,
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    )
    app.logger.addHandler(file_handler)
