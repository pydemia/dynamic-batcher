from typing import Optional, Dict
import logging
from logging.config import dictConfig
from logging.config import fileConfig
import threading
import os
import sys
import json


__all__ = [
    "LOGGERNAME_BATCHPROCESSOR",
    "Logger",
]

# # syslog facility codes
# SYSLOG_FACILITIES = {
#     "auth": 4,
#     "authpriv": 10,
#     "cron": 9,
#     "daemon": 3,
#     "ftp": 11,
#     "kern": 0,
#     "lpr": 6,
#     "mail": 2,
#     "news": 7,
#     "security": 4,  # DEPRECATED
#     "syslog": 5,
#     "user": 1,
#     "uucp": 8,
#     "local0": 16,
#     "local1": 17,
#     "local2": 18,
#     "local3": 19,
#     "local4": 20,
#     "local5": 21,
#     "local6": 22,
#     "local7": 23
# }


def get_config_defaults(level: str = "info") -> Dict:

    CONFIG_DEFAULTS = {
        "version": 1,
        "disable_existing_loggers": False,
        # "root": {"level": level, "handlers": ["console"]},
        "loggers": {
            "batch_processor": {
                "level": level,
                "handlers": ["console"],
                "propagate": True,
                "qualname": "batch_processor"
            },
            "batch_processor.error": {
                "level": level,
                "handlers": ["error_console"],
                "propagate": True,
                "qualname": "batch_processor.error"
            },

            "batch_processor.access": {
                "level": level,
                "handlers": ["console"],
                "propagate": True,
                "qualname": "batch_processor.access"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "generic",
                "stream": "ext://sys.stdout"
            },
            "error_console": {
                "class": "logging.StreamHandler",
                "formatter": "generic",
                "stream": "ext://sys.stderr"
            },
        },
        "formatters": {
            "generic": {
                "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
                "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
                "class": "logging.Formatter"
            }
        }
    }
    return CONFIG_DEFAULTS


LOGGERNAME_BATCHPROCESSOR = "batch_processor"


class Logger:

    LOG_LEVELS = {
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG
    }
    loglevel = logging.INFO

    logformat = "%(asctime)s [%(process)d] [%(levelname)s] %(message)s"
    dateformat = "[%Y-%m-%d %H:%M:%S %z]"

    def __init__(
            self,
            level: str = "info",
            log_config_file: Optional[str] = None,
            log_config_json: Optional[str] = None,
            log_config_dict: Optional[Dict] = None,
        ) -> None:

        self.loglevel = self.LOG_LEVELS.get(level.lower(), logging.INFO)

        if log_config_file:
            if os.path.exists(log_config_file):
                defaults = get_config_defaults(level=self.loglevel).copy()
                defaults["__file__"] = log_config_file
                defaults["here"] = os.path.dirname(log_config_file)
                fileConfig(
                    log_config_file,
                    defaults=defaults,
                    disable_existing_loggers=False,
                )
            else:
                raise FileNotFoundError(f"Log config file '{log_config_file}' not found")
        elif log_config_json:
            self._set_log_config_dict(json.load(log_config_json))
        elif log_config_dict:
            self._set_log_config_dict(log_config_dict)
        else:
            dictConfig(get_config_defaults(level=self.loglevel))
            # raise RuntimeError("No log configuration provided: 'log_config_file' or 'log_config_dict' is needed.")

    def _set_log_config_dict(self, log_config_dict: Dict) -> None:
        config = get_config_defaults(level=self.loglevel).copy()
        config.update(log_config_dict)
        try:
            dictConfig(config)
        except (
                AttributeError,
                ImportError,
                ValueError,
                TypeError
        ) as exc:
            raise RuntimeError(str(exc))

