import logging
from src.constants import COLORS, RESET

_logger: logging.Logger | None = None

class _ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        color = COLORS.get(record.levelno, "")
        record.levelname = f"{color}{record.levelname}{RESET}"
        return super().format(record)


def get_logger(name: str = "resume_parser") -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger

    handler = logging.StreamHandler()
    handler.setFormatter(
        _ColorFormatter(
            fmt="%(asctime)s  %(levelname)-s  %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    _logger = logging.getLogger(name)
    _logger.setLevel(logging.DEBUG)
    _logger.addHandler(handler)
    _logger.propagate = False

    return _logger
