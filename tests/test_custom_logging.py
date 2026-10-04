import logging
import os

import pytest
from tests.conftest import LogCapture

from fastapi_todos.custom_logging import init_logging

logger = logging.getLogger("fastapi_todos.tests.logging_probe")


def test_exception_log_is_valid_json_with_traceback(log_capture: LogCapture) -> None:
    """A logged exception must serialize; today it raises TypeError and the
    stack trace is silently dropped."""
    init_logging()

    try:
        raise ValueError("boom")
    except ValueError:
        logger.exception("operation failed")

    records = log_capture.records()
    assert len(records) == 1, f"expected 1 record, got {records!r}"
    assert records[0]["message"] == "operation failed"
    assert records[0]["exception"]["type"] == "ValueError"
    assert records[0]["exception"]["value"] == "boom"
    assert "raise ValueError" in records[0]["exception"]["traceback"]


def test_exception_log_through_stdlib_logger_is_valid_json(
    log_capture: LogCapture,
) -> None:
    """The same must hold for records arriving via the stdlib bridge, which is
    how uvicorn and gunicorn log."""
    init_logging()

    try:
        raise ValueError("bridge boom")
    except ValueError:
        logging.getLogger("uvicorn.error").exception("uvicorn style failure")

    records = log_capture.records()
    assert len(records) == 1, f"expected 1 record, got {records!r}"
    assert records[0]["exception"]["type"] == "ValueError"
    assert records[0]["exception"]["value"] == "bridge boom"
    assert "raise ValueError" in records[0]["exception"]["traceback"]


def test_stdlib_record_is_attributed_to_the_calling_function(
    log_capture: LogCapture,
) -> None:
    """Attribution currently lands on logging/__init__.py: callHandlers."""
    init_logging()

    logging.getLogger("uvicorn.error").info("attribution probe")

    records = log_capture.records()
    assert len(records) == 1
    assert records[0]["function"] == "test_stdlib_record_is_attributed_to_the_calling_function"
    assert records[0]["file"]["name"] == os.path.basename(__file__)


def test_access_log_records_reach_the_sink(log_capture: LogCapture) -> None:
    """uvicorn.access keeps propagate=False and is left handler-less by
    init_logging, so every request log is dropped."""
    init_logging()

    logging.getLogger("uvicorn.access").info('127.0.0.1 - "GET /health HTTP/1.1" 200')

    records = log_capture.records()
    assert len(records) == 1, f"access record dropped: {records!r}"
    assert records[0]["message"] == '127.0.0.1 - "GET /health HTTP/1.1" 200'
    assert records[0]["level"] == "INFO"


def test_lowercase_log_level_does_not_crash_startup(
    monkeypatch: pytest.MonkeyPatch, log_capture: LogCapture
) -> None:
    """LOG_LEVEL=info (gunicorn's own default) currently raises ValueError on
    import and the app never starts."""
    monkeypatch.setenv("LOG_LEVEL", "info")
    init_logging()

    logger.info("still alive")

    assert log_capture.messages() == ["still alive"]


def test_lowercase_warning_log_level_does_not_crash_startup(
    monkeypatch: pytest.MonkeyPatch, log_capture: LogCapture
) -> None:
    """'warn' is valid stdlib/gunicorn but is not a Loguru level name."""
    monkeypatch.setenv("LOG_LEVEL", "warn")
    init_logging()

    logger.warning("still alive")

    assert log_capture.messages() == ["still alive"]


def test_uppercase_log_level_is_honored(
    monkeypatch: pytest.MonkeyPatch, log_capture: LogCapture
) -> None:
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    init_logging()

    logger.info("suppressed by level")
    logger.warning("emitted")

    assert log_capture.messages() == ["emitted"]


def test_invalid_log_level_falls_back_instead_of_crashing(
    monkeypatch: pytest.MonkeyPatch, log_capture: LogCapture
) -> None:
    monkeypatch.setenv("LOG_LEVEL", "not-a-level")
    init_logging()

    logger.info("still alive")

    assert log_capture.messages() == ["still alive"]
