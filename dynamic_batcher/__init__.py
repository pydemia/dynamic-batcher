import logging
import sys

from .batcher import (
    DynamicBatcher,
    BatchProcessor,
)
from . import (
    redis_engine,
    types,
)
from .types import ResponseStream, PendingRequestStream


__all__ = [
    "__version__",
    "DynamicBatcher",
    "BatchProcessor",
    "redis_engine",
    "types",
    "ResponseStream",
    "PendingRequestStream",
]

__version__ = "1.0.3"


logging.basicConfig(
    stream=sys.stdout,
)
