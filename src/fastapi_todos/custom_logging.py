# Custom Logger Using Loguru
# https://loguru.readthedocs.io/en/stable/api/logger.html


import json
import logging
import os
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


# https://loguru.readthedocs.io/en/stable/api/logger.html
def serialize(record):
    subset = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "elapsed_sec": record["elapsed"].total_seconds(),
        "exception": record["exception"]
        and {
            "type": record["exception"].type.__name__,
            "value": record["exception"].value,
            "traceback": bool(record["exception"]),
        },
        "extra": record["extra"],
        "file": {"name": record["file"].name},
        "function": record["function"],
        "line": record["line"],
        "name": record["name"],
        "process": {"id": record["process"].id, "name": record["process"].name},
        "thread": {"id": record["thread"].id, "name": record["thread"].name},
    }
    return json.dumps(subset)


def format_record(record):
    # Note this function returns the string to be formatted,
    # not the actual message to be logged
    record["extra"]["serialized"] = serialize(record)
    return "{extra[serialized]}\n"


def init_logging():
    """
    Replaces logging handlers with a handler for using the custom handler.

    WARNING!
    if you call the init_logging in startup event function,
    then the first logs before the application start will be in the old format
     app.add_event_handler("startup", init_logging)
    stdout:
    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Waiting for application startup.

    """

    # disable handlers for specific uvicorn loggers
    # to redirect their output to the default uvicorn logger
    # works with uvicorn==0.11.6
    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith(("uvicorn.", "gunicorn."))
    )
    for uvicorn_logger in loggers:
        uvicorn_logger.handlers = []

    # change handler for default uvicorn logger
    intercept_handler = InterceptHandler()
    logging.getLogger("uvicorn").handlers = [intercept_handler]

    # set logs output, level and format
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "level": os.environ.get("LOG_LEVEL", logging.DEBUG),
                "format": format_record,
                "enqueue": True,
            },
        ],
    )
