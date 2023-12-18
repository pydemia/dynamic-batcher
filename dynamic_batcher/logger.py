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

        # self.error_log = logging.getLogger("batch_processor.error")
        # self.error_log.propagate = False
        # self.error_handlers = []

        # self.access_log = logging.getLogger("batch_processor.access")
        # self.access_log.propagate = False
        # self.access_handlers = []

        # self.logfile = None
        # self.lock = threading.Lock()


        # self.loglevel = self.LOG_LEVELS.get(level.lower(), logging.INFO)
        # self.error_log.setLevel(self.loglevel)
        # self.access_log.setLevel(self.loglevel)

        # self.batchprocessor_log = logging.getLogger("batch_processor")
        # self.batchprocessor_log.propagate = False
        # self.batchprocessor_log_handlers = []

        # self.logfile = None
        # self.lock = threading.Lock()

        # self.loglevel = self.LOG_LEVELS.get(level.lower(), logging.INFO)
        # self.batchprocessor_log.setLevel(self.loglevel)


        # # set gunicorn.error handler
        # if self.cfg.capture_output and cfg.errorlog != "-":
        #     for stream in sys.stdout, sys.stderr:
        #         stream.flush()

        #     self.logfile = open(cfg.errorlog, 'a+')
        #     os.dup2(self.logfile.fileno(), sys.stdout.fileno())
        #     os.dup2(self.logfile.fileno(), sys.stderr.fileno())


        # self._set_handler(self.error_log, cfg.errorlog,
        #                   logging.Formatter(self.logformat, self.dateformat))

        # # set gunicorn.access handler
        # self._set_handler(
        #     self.access_log, cfg.accesslog,
        #     fmt=logging.Formatter(self.logformat), stream=sys.stdout
        # )

        # # set syslog handler
        # if cfg.syslog:
        #     self._set_syslog_handler(
        #         self.error_log, cfg, self.syslog_fmt, "error"
        #     )
        #     if not cfg.disable_redirect_access_to_syslog:
        #         self._set_syslog_handler(
        #             self.access_log, cfg, self.syslog_fmt, "access"
        #         )

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


#     def _set_handler(self, log, output, fmt, stream=None):

#         if output is not None:
#             if output == "-":
#                 h = logging.StreamHandler(stream)
#             else:
#                 _check_is_writable(output)
#                 h = logging.FileHandler(output)
#                 # make sure the user can reopen the file
#                 try:
#                     os.chown(h.baseFilename, os.getuid(), os.getgid())
#                 except OSError:
#                     # it's probably OK there, we assume the user has given
#                     # /dev/null as a parameter.
#                     pass

#             h.setFormatter(fmt)


#     def _set_syslog_handler(self, log, cfg, fmt, name):
#         # setup format
#         prefix = cfg.syslog_prefix or cfg.proc_name.replace(":", ".")

#         prefix = "gunicorn.%s.%s" % (prefix, name)

#         # set format
#         fmt = logging.Formatter(r"%s: %s" % (prefix, fmt))

#         # syslog facility
#         try:
#             facility = SYSLOG_FACILITIES[cfg.syslog_facility.lower()]
#         except KeyError:
#             raise RuntimeError("unknown facility name")

#         # parse syslog address
#         socktype, addr = _parse_syslog_address(cfg.syslog_addr)

#         # finally setup the syslog handler
#         h = logging.handlers.SysLogHandler(address=addr,
#                                            facility=facility, socktype=socktype)

#         h.setFormatter(fmt)
#         log.addHandler(h)


# def _parse_syslog_address(addr):

#     # unix domain socket type depends on backend
#     # SysLogHandler will try both when given None
#     if addr.startswith("unix://"):
#         sock_type = None

#         # set socket type only if explicitly requested
#         parts = addr.split("#", 1)
#         if len(parts) == 2:
#             addr = parts[0]
#             if parts[1] == "dgram":
#                 sock_type = socket.SOCK_DGRAM

#         return (sock_type, addr.split("unix://")[1])

#     if addr.startswith("udp://"):
#         addr = addr.split("udp://")[1]
#         socktype = socket.SOCK_DGRAM
#     elif addr.startswith("tcp://"):
#         addr = addr.split("tcp://")[1]
#         socktype = socket.SOCK_STREAM
#     else:
#         raise RuntimeError("invalid syslog address")

#     if '[' in addr and ']' in addr:
#         host = addr.split(']')[0][1:].lower()
#     elif ':' in addr:
#         host = addr.split(':')[0].lower()
#     elif addr == "":
#         host = "localhost"
#     else:
#         host = addr.lower()

#     addr = addr.split(']')[-1]
#     if ":" in addr:
#         port = addr.split(':', 1)[1]
#         if not port.isdigit():
#             raise RuntimeError("%r is not a valid port number." % port)
#         port = int(port)
#     else:
#         port = 514

#     return (socktype, (host, port))

# def _check_is_writable(path):
#     try:
#         with open(path, 'a') as f:
#             f.close()
#     except IOError as e:
#         raise RuntimeError("Error: '%s' isn't writable [%r]" % (path, e))