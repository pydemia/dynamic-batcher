from typing import List, Dict, NamedTuple


__all__ = [
    "ResponseStream",
    "PendingRequestStream",
]


class ResponseStream(NamedTuple):
    stream_id: bytes
    body: List | Dict


class PendingRequestStream(NamedTuple):
    message_id: bytes
    consumer: bytes
    time_since_delivered: int
    times_delivered: int