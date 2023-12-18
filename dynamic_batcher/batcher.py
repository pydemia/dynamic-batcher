"""
====================================
 :mod:`batcher` Module
====================================
.. moduleauthor:: Youngju Jaden Kim <pydemia@gmail.com>
.. note:: Info

Info
====
    `DynamicBatcher` and `BatchProcessor`

"""


from typing import Optional, List, Dict, Callable, NamedTuple
import os
import json
import logging
import asyncio
import redis
from autologging import logged
from . import logger

from .redis_engine import (
    REDIS__HOST,
    REDIS__PORT,
    REDIS__DB,
    REDIS__PASSWORD,
    REDIS__STREAM_KEY_REQUEST,
    REDIS__STREAM_GROUP_PROCESSOR,
    REDIS__STREAM_KEY_RESPONSE,
    REDIS__STREAM_GROUP_BATCHER,
    get_client,
)
from .types import ResponseStream, PendingRequestStream


__all__ = [
    "DynamicBatcher",
    "BatchProcessor",
]


DYNAMIC_BATCHER__BATCH_SIZE = int(os.getenv("DYNAMIC_BATCHER__BATCH_SIZE", "64"))
DYNAMIC_BATCHER__BATCH_TIME = int(os.getenv("DYNAMIC_BATCHER__BATCH_TIME", "2"))


# logging.config.dictConfig(CONFIG_DEFAULTS)
# logger.Logger(level="DEBUG")


@logged
class DynamicBatcher:
    """A Client class for dynamic batch processing.
    A `DynamicBatcher` tries to connect a redis server with connection info., given by the following ``ENVVAR``:

        .. code-block:: bash

            REDIS__HOST=localhost
            REDIS__PORT=6379
            REDIS__DB=0
            REDIS__PASSWORD=

    Args:
        delay (int):
            Seconds of frequency to parse a response, corresponding a request sent. Defaults to ``0.01``.
        
        timeout (int):
            Seconds of deadline to wait for a response. Defaults to ``100``.
            If `timeout` is too large, it will be stuck on waiting too long, which is not intended.
            If `timeout` is too small, it will work as impatient, not waiting for the batch process is finished.
    
    Attributes:
        delay (int):
            Seconds of frequency to parse a response, corresponding a request sent.
        timeout (int):
            Seconds of deadline to wait for a response.

    Example:
        Create a `batcher`:
            >>> from dynamic_batcher import DynamicBatcher
            >>> batcher = DynamicBatcher()
        
        You can give some parameters:
            >>> lazy_batcher = DynamicBatcher(delay=1)
        
        Or, create a fail-fast `batcher`:
            >>> fail_fast_batcher = DynamicBatcher(timeout=3)
    
    Raises:
        redis.exceptions.ConnectionError: a redis server is not available.

    """
    def __init__(
            self,
            # host: str = "localhost",
            # port: int = 6379,
            # db: int = 0,
            # password: Optional[str] = None,
            # key="infer",
            # group="infergrp",
            delay: int = 0.01,
            timeout: int = 100,
        ):
        self.log = self.__log or logging.getLogger(self.__class__.__qualname__)

        self._redis_client = get_client(
            host=REDIS__HOST,
            port=REDIS__PORT,
            db=REDIS__DB,
            password=REDIS__PASSWORD,
        )
        self._request_key: str = REDIS__STREAM_KEY_REQUEST
        self._response_key: str = REDIS__STREAM_KEY_RESPONSE
        self._processor_group: str = REDIS__STREAM_GROUP_PROCESSOR
        self._batcher_group: str = REDIS__STREAM_GROUP_BATCHER

        self.delay = delay
        self.timeout = timeout

    async def asend(self, body: Dict|List, *args, **kwargs) -> Optional[Dict|List]:
        """Send a request and wait for a response, with JSON-serializable body.

        Args:
            body (:obj: ``Dict`` or ``List``): A **JSON-serializable object**, especially ``Dict`` or ``List``.
            \*args: Variable length argument list.
            \**kwargs: Arbitrary keyword arguments.
        
        Returns:
            Dict or List: optional
        
        Example:

            >>> import time
            >>> import uvicorn
            >>> from typing import List
            >>> from fastapi import FastAPI
            >>> from pydantic import BaseModel
            >>> from dynamic_batcher import DynamicBatcher
            >>> 
            >>> app = FastAPI()
            >>> batcher = DynamicBatcher()
            >>> class RequestItem(BaseModel):
            ...     key: str
            ...     values: List[int] = [1, 5, 2]
            >>> 
            >>> @app.post("/batch/{key}")
            >>> async def run_batch(key: str, body: RequestItem):
            ...     start_time = time.time()
            ...     resp_body = await batcher.asend(body.model_dump())
            ...     result = {
            ...         "key": key,
            ...         "values": body.values,
            ...         "values_sum": resp_body,
            ...         "elapsed": time.time() - start_time
            ...     }
            ...     return result
            >>> 
            >>> if __name__ == "__main__":
            >>>     uvicorn.run(app)
            INFO:     Started server process [27085]
            INFO:     Waiting for application startup.
            INFO:     Application startup complete.
            INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
        """
        try:
            json_body = json.dumps(body)
        except json.JSONDecodeError as json_e:
            self.log.error(f"cannot serialize request body: {json_e}\n{json_e.with_traceback}")
            return
        try:
            requested_stream_id: bytes = self._redis_client.xadd(self._request_key, {"body": json_body})
            r = await self._wait_for_start(requested_stream_id, delay=self.delay, timeout=self.timeout)
            r = await self._wait_for_finish(requested_stream_id, delay=self.delay, timeout=self.timeout)
            return r.body
        except redis.RedisError as redis_e:
            self.log.error(f"redis not available: {redis_e}\n{redis_e.with_traceback}")
            return
        except json.JSONDecodeError as json_e:
            self.log.error(f"cannot de-serialize response body: {json_e}\n{json_e.with_traceback}")
            return
        except Exception as unknown_e:
            self.log.error(f"failed to respond (unknown): {unknown_e}")
            return


    async def _wait_for_start(self, stream_id: bytes, delay: int = 0.1, timeout=10) -> Optional[ResponseStream]:
        is_accepted = False
        total_delay = 0
        while is_accepted or (total_delay < timeout):
            r = self._get_request_accepted(stream_id)
            if r:
                is_accepted = True
                break
            await asyncio.sleep(delay)
            total_delay += delay
        return r

    async def _wait_for_finish(self, stream_id: bytes, delay: int = 0.1, timeout=10) -> Optional[ResponseStream]:
        is_arrived = False
        total_delay = 0
        while is_arrived or (total_delay < timeout):
            r = self._get_response_arrived_as_record(stream_id)
            if r:
                is_arrived = True
                break
            await asyncio.sleep(delay)
            total_delay += delay
        return r

    def _get_request_accepted(self, stream_id: bytes) -> Optional[bytes]:
        messages: List = self._redis_client.xpending_range(
            self._request_key,
            groupname=self._processor_group,
            count=1,
            min=stream_id,
            max=stream_id,
        )
        if messages:
            message = PendingRequestStream(**messages[0])
            pending_time = (message.time_since_delivered - message.times_delivered) / 1000
            return message.message_id
        else:
            return

    def _get_response_arrived_as_record(self, stream_id: bytes) -> Optional[ResponseStream]:
        message: Optional[str] = self._redis_client.get(stream_id)
        if message:
            _body = json.loads(message)
            self._redis_client.delete(stream_id)
            return ResponseStream(stream_id, _body)
        else:
            return

    def _get_response_arrived_as_stream(self, stream_id: bytes) -> Optional[ResponseStream]:
        message: Optional[Dict] = self._redis_client.get(stream_id)
        messages: List = self._redis_client.xrange(
            self._response_key,
            min=stream_id,
            max=stream_id,
        )
        if messages:
            message = messages[0]
            _id, _body = message
            self._redis_client.xack(self._response_key, self._batcher_group, _id)
            self._redis_client.xdel(self._response_key, _id)
            return ResponseStream(_id, _body)
        else:
            return


class BatchProcessor:
    """A Client class for dynamic batch processing.
    A `BatchProcessor` tries to connect a redis server with connection info., given by the following ``ENVVAR``:

        .. code-block:: bash

            REDIS__HOST=localhost
            REDIS__PORT=6379
            REDIS__DB=0
            REDIS__PASSWORD=
            
            DYNAMIC_BATCHER__BATCH_SIZE=64
            DYNAMIC_BATCHER__BATCH_TIME=2

    Args:
        batch_size (int):
            Number of requests for a batch. Defaults to ``64``.
            If ``DYNAMIC_BATCHER__BATCH_SIZE`` is set, the argument default value is overrided.
            When the argument value is passed, all other settings are ignored.

            Priority::
    
                values passed > ENVVAR > default value
        

        batch_time (int):
            Seconds of deadline to wait for requests. Defaults to ``2``.
            If `timeout` is too large, it will be stuck on waiting too long, which is not intended.
            If `timeout` is too small, it will work as impatient, not waiting for the batch process is finished.
    
    Attributes:
        delay (int):
            Seconds of frequency to parse a request.
        
        batch_size (int):
            Number of requests for a batch.
        
        batch_time (int):
            Seconds of deadline to wait for requests.

    Example:
        Create a `processor`:
            >>> import asyncio
            >>> from dynamic_batcher import BatchProcessor
            >>> processor = BatchProcessor()
            >>> asyncio.run(batch_processor.start_daemon(lambda x: x))

    Raises:
        redis.exceptions.ConnectionError: a redis server is not available.
    """

    def __init__(
            self,
            batch_size: int = DYNAMIC_BATCHER__BATCH_SIZE or 64,
            batch_time: int = DYNAMIC_BATCHER__BATCH_TIME or 2,
        ):

        self.log = logging.getLogger(logger.LOGGERNAME_BATCHPROCESSOR)
        self.log.info("LOG_LEVEL: %s", logging.getLevelName(self.log.level))
        self.delay = 0.001
        self.batch_size = batch_size
        self.batch_time = batch_time
        self._redis_client = get_client(
            host=REDIS__HOST,
            port=REDIS__PORT,
            db=REDIS__DB,
            password=REDIS__PASSWORD,
        )
        self._request_key = REDIS__STREAM_KEY_REQUEST
        self._response_key = REDIS__STREAM_KEY_RESPONSE
        self._processor_group = REDIS__STREAM_GROUP_PROCESSOR
        self._batcher_group = REDIS__STREAM_GROUP_BATCHER

        self.response_expiration_sec = 600
    async def start_daemon(self, func: Callable) -> None:
        """Start a single batch process as a daemon.
        This will concatenate given requests to one batch, call `func`, and split into corresponding responses.

        Args:
            func (:obj: `Callable`): A callable object, like function or method.
                `func` should have only one positional argument, and its type should be ``List``; to handle the argument as a scalable batch.
                The type of the argument and the returning value should be ``List``, to handle a scalable batch and operate elementwisely.
                Also both argument and returning value should be **JSON (de)serializable**.

        Returns:
            None
        
        Example:

            First, define a function to run:

                >>> import asyncio
                >>> from dynamic_batcher import BatchProcessor
                >>> from typing import List, Dict
                >>> body_list = [
                ...     {'values': [1, 2, 3]},
                ...     {'values': [4, 5, 6]}
                ... ]
                >>> def sum_values(bodies: List[Dict]) -> List[Dict]:
                ...     result = []
                ...     for body in bodies:
                ...         result.append( { 'sum': sum(body['values']) } )
                ...     return result
                    
                >>> sum_values(body_list)
                [{'sum': 6}, {'sum': 15}]
            
            Then, run a ``BatchProcessor``:

                >>> import asyncio
                >>> from dynamic_batcher import BatchProcessor
                >>> batch_processor = BatchProcessor()
                >>> asyncio.run(batch_processor.start_daemon(sum_values))
            
            
        """
        self.log.info(
            ' '.join([
                'BatchProcessor start:',
                f'delay={self.delay},',
                f'batch_size={self.batch_size}',
                f'batch_time={self.batch_time}',
            ])
        )
        while True:
            await self._run(func)
            await self._trim()


    async def _run(self, func: Callable) -> None:
        delay_period = 0
        batch_gathered = 0
        requests = []
        while delay_period < self.batch_time and batch_gathered < self.batch_size:
            # self.log.debug(
            #     f'alive: {delay_period:.3f}/{self.batch_time}, {batch_gathered}/{self.batch_size}'
            # )
            new_request = await self._get_next_request()
            if new_request:
                requests.extend(new_request)

            batch_gathered = len(requests)
            delay_period += self.delay

            await asyncio.sleep(self.delay)

        if requests:
            self.log.debug(
                f'batch start: {delay_period:.3f}/{self.batch_time}, {batch_gathered}/{self.batch_size}'
            )
            streams = [v[0] for i, v in requests]
            streams = sorted(streams, key=lambda x: x[0])
            stream_ids = [i for i, v in streams]
            stream_bodies = [json.loads(v['body']) for i, v in streams]

            try:
                results = func(stream_bodies)
            except Exception as e:
                self.log.error(f'Error while running `{func.__name__}`: {e}')
                results = None

            await self._mark_as_finished_as_record(stream_ids, results)


    async def _mark_as_finished_as_record(self, stream_ids: List[str], results: Optional[List[Dict]]) -> None:
        for stream_id, stream_body in zip(stream_ids, results):
            self._redis_client.set(
                stream_id,
                json.dumps(stream_body),
                ex=self.response_expiration_sec,
            )

        self._redis_client.xdel(self._request_key, *stream_ids)


    async def _mark_as_finished_as_stream(self, stream_ids: List[str], results: Optional[List[Dict]]) -> None:
        if results is None:
            results = [None for i in stream_ids]
        for stream_id, stream_body in zip(stream_ids, results):
            self._redis_client.xadd(
                self._response_key,
                stream_body,
                stream_id,
            )
        # self._redis_client.xack(self.request_key, self.processor_group, *stream_ids)
        self._redis_client.xdel(self._request_key, *stream_ids)


    async def _get_next_request(self) -> Optional[List]:

        try:
            requests: List = self._redis_client.xreadgroup(
                groupname=self._processor_group,
                consumername=self._processor_group,
                streams={self._request_key: '>'},
                count=1,
                # block=self.batch_time,
                noack=False,
            )
            if requests:
                return requests
            else:
                return

        except Exception as e:
            self.log.error(f'Error while reading message {e}')

    async def _trim(self) -> None:
        try:
            remaining_msg_cnt = self.batch_size * 10
            request_trimmed_cnt: int = self._redis_client.xtrim(
                self._request_key,
                maxlen=remaining_msg_cnt,
            )
            self.log.debug(f'Trimmed old requests: {request_trimmed_cnt}')

            response_trimmed_cnt: int = self._redis_client.xtrim(
                self._response_key,
                maxlen=remaining_msg_cnt,
            )
            self.log.debug(f'Trimmed old responses: {response_trimmed_cnt}')

        except Exception as e:
            self.log.error(f'Error while trimming message {e}'
            )