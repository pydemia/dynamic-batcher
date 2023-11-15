from typing import List, Dict, NamedTuple


__all__ = [
    "ResponseStream",
    "PendingRequestStream",
]


class ResponseStream(NamedTuple):
    """(Internally used) DTO Class for Response.

    Example:
        
        assign case 1:
            >>> stream = ResponseStream(stream_id=b'1234', body={'values': [1, 2, 3]})

        assign case 2:
            >>> response = {'stream_id': b'1234', 'body': {'values': [1, 2, 3]}}
            >>> stream = ResponseStream(**response)

        dump:
            >>> stream = ResponseStream(stream_id=b'1234', body={'values': [1, 2, 3]})
            >>> response = stream.model_dump()
            >>> response
            {'stream_id': b'1234', 'body': {'values': [1, 2, 3]}}

    """
    stream_id: bytes
    body: List | Dict


class PendingRequestStream(NamedTuple):
    """(Internally used) DTO Class for Request.

    Example:
        
        assign case 1:
            >>> stream = PendingRequestStream(
            ...     message_id=b'1234',
            ...     consumer=b'consumer',
            ...     time_since_delivered=11234,
            ...     times_delivered=1,
            ... )
        
        assign case 2:
            >>> request = {    
            ...     'message_id': b'1234',
            ...     'consumer': b'consumer',
            ...     'time_since_delivered': 11234,
            ...     'times_delivered': 1,
            ... }
            >>> stream = ResponseStream(**request)
            {'stream_id': b'1234', 'body': {'values': [1, 2, 3]}}
            >>> stream = ResponseStream(**request)

        dump:
            >>> stream = PendingRequestStream(
            ...     message_id=b'1234',
            ...     consumer=b'consumer',
            ...     time_since_delivered=11234,
            ...     times_delivered=1,
            ... )
            >>> request = stream.model_dump()
            >>> request
            {'message_id': b'1234', 'consumer': b'consumer', 'time_since_delivered': 11234, 'times_delivered': 1}

    """
    message_id: bytes
    consumer: bytes
    time_since_delivered: int
    times_delivered: int