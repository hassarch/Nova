"""Session-based logger factory for NOVA."""

import logging
from datetime import datetime
from pathlib import Path

LOG_DIR = Path.home() / ".nova" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def create_session_logger():
    """Create a session-based logger with file and console handlers.

    Returns:
        tuple: (logger, log_file_path)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"session_{timestamp}.log"

    logger = logging.getLogger(f"nova_session_{timestamp}")
    logger.setLevel(logging.DEBUG)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger, log_file
