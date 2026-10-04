# Structured JSON logging on the standard library.
# https://docs.python.org/3/library/logging.html

from __future__ import annotations

import json
import logging
import os
import sys
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path
from types import TracebackType
from typing import Any

# logging.LogRecord.exc_info, as stdlib actually populates it: a real
# (type, value, traceback) triple, or the literal (None, None, None).
_ExcInfo = tuple[type[BaseException], BaseException, TracebackType | None] | tuple[None, ...]

DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVELS = (
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
)

# Loggers whose records we take over. uvicorn.access sets propagate=False, so
# it needs the handler attached explicitly or its records go nowhere.
MANAGED_LOGGERS = ("uvicorn", "uvicorn.error", "uvicorn.access", "gunicorn", "gunicorn.error")

# The field names logging sets on every record; anything else came from extra=.
RESERVED_RECORD_FIELDS = frozenset(
    logging.LogRecord("", 0, "", 0, "", (), None).__dict__
)

# Wall-clock reference for elapsed_sec, set by init_logging().
_STARTED_AT = time.monotonic()


def resolve_log_level(raw: str | None) -> str:
    """Normalize a LOG_LEVEL env value to a stdlib level name.

    Gunicorn and stdlib logging spell levels lowercase ("info", "warn"), and
    logging.Logger.setLevel raises ValueError on anything but a known name --
    which would abort startup. Unknown values fall back to the default.
    """
    if not raw:
        return DEFAULT_LOG_LEVEL
    candidate = raw.strip().upper()
    if candidate in LOG_LEVELS:
        return candidate
    # stdlib accepts the WARN alias that has no WARN attribute name.
    if candidate == "WARN":
        return "WARNING"
    return DEFAULT_LOG_LEVEL


def format_exception(exc_info: _ExcInfo) -> str:
    """Render an exception as text.

    stdlib hands us the (type, value, traceback) tuple already joined up, so
    this is a single traceback.format_exception call rather than loguru's
    three-part reassembly.
    """
    exc_type, exc_value, exc_tb = exc_info
    if exc_type is None or exc_value is None or exc_tb is None:
        return ""
    return "".join(traceback.format_exception(exc_type, exc_value, exc_tb))


class JsonFormatter(logging.Formatter):
    """Render each record as one line of JSON.

    The key names match the loguru-era output (timestamp, level, message,
    elapsed_sec, exception, extra, file, function, line, name, process,
    thread) so existing log consumers see no schema change.
    """

    def format(self, record: logging.LogRecord) -> str:
        # Anything passed via extra= lands on the record's __dict__ but is not
        # one of logging's own reserved fields; those become "extra". Built once
        # per process since the reserved set is fixed by the LogRecord class.
        extra = {k: v for k, v in record.__dict__.items() if k not in RESERVED_RECORD_FIELDS}

        exc_info: _ExcInfo = record.exc_info or (None, None, None)
        exc_type, exc_value, _ = exc_info
        exception = (
            {
                "type": exc_type.__name__,
                # str(), not the object: json.dumps cannot encode an exception
                # instance and would drop the whole record.
                "value": str(exc_value),
                "traceback": format_exception(exc_info),
            }
            if exc_type is not None
            else None
        )

        subset: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "elapsed_sec": time.monotonic() - _STARTED_AT,
            "exception": exception,
            # uvicorn tags most of its records with an ANSI-colored duplicate, which
            # arrives here as escaped bytes and bloats the payload.
            "extra": {
                k: v for k, v in extra.items() if k != "color_message"
            },
            "file": {"name": Path(record.pathname).name},
            "function": record.funcName,
            "line": record.lineno,
            "name": record.name,
            "process": {"id": record.process, "name": record.processName},
            "thread": {"id": record.thread, "name": record.threadName},
        }
        # No trailing newline: StreamHandler appends its own terminator, and
        # doing both leaves a blank line after every record.
        return json.dumps(subset)


def init_logging() -> None:
    """Route this app's and uvicorn's/gunicorn's logging to stdout as JSON.

    Safe to call more than once -- main.py calls it at import and the tests
    call it per test. Existing handlers on the managed loggers are removed
    first, so repeated calls replace the sink rather than stacking duplicates.
    """
    global _STARTED_AT

    log_level = resolve_log_level(os.environ.get("LOG_LEVEL"))

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    for name in MANAGED_LOGGERS:
        target = logging.getLogger(name)
        # Clearing their own handlers and re-attaching covers every child
        # logger too; propagate stays False so records don't double up through
        # the root logger.
        target.handlers = [handler]
        target.propagate = False
        target.setLevel(log_level)

    # Our own modules log through the root logger's hierarchy by name.
    root = logging.getLogger("fastapi_todos")
    root.handlers = [handler]
    root.propagate = False
    root.setLevel(log_level)

    _STARTED_AT = time.monotonic()