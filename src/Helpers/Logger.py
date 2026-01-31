import logging
from datetime import datetime
from typing import Any


class CustomFormatter(logging.Formatter):
    COLORS: dict[str, str] = {
        "DEBUG": "\033[92m",  # Green
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[91m",  # Red
        "NOTICE": "\033[92m",  # Green (custom level)
        "RESET": "\033[0m",
    }

    def format(self, record: logging.LogRecord) -> str:
        log_color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"{log_color}{log_time} - {record.levelname} - {record.getMessage()}{self.COLORS['RESET']}"
        return formatted_message


NOTICE_LEVEL_NUM = 25
logging.addLevelName(NOTICE_LEVEL_NUM, "NOTICE")


def notice(
    self: logging.Logger, message: Any, *args: Any, **kwargs: Any
) -> None:
    if self.isEnabledFor(NOTICE_LEVEL_NUM):
        self._log(NOTICE_LEVEL_NUM, message, args, **kwargs)


# Add `notice()` to Logger class
logging.Logger.notice = notice  # type: ignore[attr-defined]


def get_logger() -> logging.Logger:
    logger = logging.getLogger("custom_logger")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(CustomFormatter())
        logger.addHandler(ch)

    return logger
