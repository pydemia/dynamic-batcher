import logging
import sys

from .batcher import (
    DynamicBatcher,
    BatchProcessor,
)
from . import redis_engine


__all__ = [
    "__version__",
    "DynamicBatcher",
    "BatchProcessor",
    "redis_engine",
]

__version__ = "1.0.0"


logging.basicConfig(
    stream=sys.stdout,
)
