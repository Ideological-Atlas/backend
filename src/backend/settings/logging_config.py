import logging
import os
import sys
import warnings

from .base import BASE_DIR, PROJECT_NAME, join

LOG_DIR = join(BASE_DIR, "../logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[%(asctime)s] %(levelname)s (%(name)s) %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file_main": {
            "level": "INFO",
            "class": "logging.handlers.WatchedFileHandler",
            "filename": join(LOG_DIR, f"{PROJECT_NAME}.log"),
            "formatter": "simple",
        },
    },
    "loggers": {
        "": {"handlers": ["console", "file_main"], "level": "INFO"},
        "django": {
            "handlers": ["console", "file_main"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

warnings.filterwarnings(
    "ignore",
    message="StreamingHttpResponse must consume synchronous iterators",
    module="django.core.handlers.asgi",
)

if len(sys.argv) > 1 and sys.argv[1] == "test":
    logging.disable(logging.CRITICAL)
