"""
logging_config.py — structured logging configuration.

Sets up Python's standard logging module to output JSON-formatted log lines
in production and human-readable lines in development.

Why structured (JSON) logging?
  In production, logs go to a log aggregator (Papertrail, Datadog, CloudWatch).
  These tools can parse JSON fields and let you filter by request_id, status_code,
  path, etc. Plain text logs make that much harder.

Why keep human-readable in development?
  JSON logs are hard to read in a terminal. The format switches based on the
  ENVIRONMENT setting so local development stays readable.

Usage:
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Something happened", extra={"node_id": str(node_id)})

The request_id is injected by the RequestIDMiddleware in middleware.py
and is available on every log line automatically.
"""
import json
import logging
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """
    Formats log records as single-line JSON objects.
    Extra fields passed via logger.info(..., extra={...}) are included.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include any extra fields attached to the record
        for key, value in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "taskName",
            ):
                log_obj[key] = value

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


class HumanFormatter(logging.Formatter):
    """
    Human-readable format for development.
    Example: 2024-01-15 12:34:56 | INFO  | main | Server started
    """
    COLOURS = {
        "DEBUG": "\033[36m",     # cyan
        "INFO": "\033[32m",      # green
        "WARNING": "\033[33m",   # yellow
        "ERROR": "\033[31m",     # red
        "CRITICAL": "\033[35m",  # magenta
        "RESET": "\033[0m",
    }

    def format(self, record: logging.LogRecord) -> str:
        colour = self.COLOURS.get(record.levelname, "")
        reset = self.COLOURS["RESET"]
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        level = f"{colour}{record.levelname:<8}{reset}"
        request_id = getattr(record, "request_id", "")
        rid = f" [{request_id[:8]}]" if request_id else ""
        return f"{ts} | {level} | {record.name}{rid} | {record.getMessage()}"


def configure_logging(environment: str = "development") -> None:
    """
    Configure the root logger based on the current environment.
    Call this once at application startup.
    """
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Remove any existing handlers (e.g. from uvicorn)
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if environment == "production":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(HumanFormatter())

    root.addHandler(handler)

    # Quieten noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
