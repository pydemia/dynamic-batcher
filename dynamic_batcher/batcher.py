from typing import Optional, List, Dict, Callable, Any, NamedTuple
import os
import json
import redis
import asyncio
from autologging import logged
from redis.exceptions import (
    ConnectionError,
    DataError,
    NoScriptError,
    RedisError,
    ResponseError,
)

from .redis_engine import (
    USE_LOCAL_REDIS,
    REDIS__HOST,
    REDIS__PORT,
    REDIS__DB,
    REDIS__PASSWORD,
    REDIS__STREAM_KEY_REQUEST,
    REDIS__STREAM_GROUP_PROCESSOR,
    REDIS__STREAM_KEY_RESPONSE,
    REDIS__STREAM_GROUP_BATCHER,
    # launch,
    info,
    get_client,
)


__all__ = [
    "DynamicBatcher",
    "BatchProcessor",
]


# REDIS__HOST = os.getenv("REDIS__HOST", "localhost")
# REDIS__PORT = int(os.getenv("REDIS__PORT", "6379"))
# REDIS__DB = int(os.getenv("REDIS__DB", "0"))
# REDIS__PASSWORD = os.getenv("REDIS__PASSWORD", None)
# REDIS__STREAM_KEY = os.getenv("REDIS__STREAM_KEY", "skey")
# REDIS__STREAM_GROUP = os.getenv("REDIS__STREAM_GROUP", "sgroup")


# if bool(USE_LOCAL_REDIS):
#     launch()

class StreamBody(NamedTuple):
    stream_id: bytes
    body: List | Dict

class Message(NamedTuple):
    message_id: bytes
    consumer: bytes
    time_since_delivered: int
    times_delivered: int

@logged
class DynamicBatcher:
    def __init__(
            self,
            # host: str = "localhost",
            # port: int = 6379,
            # db: int = 0,
            # password: Optional[str] = None,
            # key="infer",
            # group="infergrp",
            delay: int = 0.1,
            timeout: int = 100,
        ):
        self._redis_client = get_client(
            host=REDIS__HOST,
            port=REDIS__PORT,
            db=REDIS__DB,
            password=REDIS__PASSWORD,
        )
        self.request_key = REDIS__STREAM_KEY_REQUEST
        self.response_key = REDIS__STREAM_KEY_RESPONSE
        self.processor_group = REDIS__STREAM_GROUP_PROCESSOR
        self.batcher_group = REDIS__STREAM_GROUP_BATCHER

        self.delay = delay
        self.timeout = timeout

    # def set_key_value(self, key: str, value) -> bool:
    #     return self._redis_client.set(key=key, value=value)
    
    # def info_group(self):
    #     return self._redis_client.xinfo_groups(self.group)
    
    # def info_key(self):
    #     return self._redis_client.xinfo_stream(self.key)
    
    # def info_consumer(self):
    #     return self._redis_client.xinfo_consumers(self.key, self.group)

    async def asend(self, body: Dict, *args, **kwargs) -> Optional[StreamBody]:
        # requested_stream_id: bytes = self._redis_client.xadd(self.request_key, {'body': json.dumps(body)})
        requested_stream_id: bytes = self._redis_client.xadd(self.request_key, body)
        r = await self._wait_for_start(requested_stream_id, delay=self.delay, timeout=self.timeout)
        r = await self._wait_for_finish(requested_stream_id, delay=self.delay, timeout=self.timeout)
        return r

    
    def get_stream_by_id(self, stream_id: bytes) -> Optional[StreamBody]:
        messages: List = self._redis_client.xrange(
            self.request_key,
            min=stream_id,
            max=stream_id,
        )
        if messages:
            return StreamBody(stream_id, messages)
        else:
            return

    async def _wait_for_start(self, stream_id: bytes, delay: int = 0.1, timeout=10) -> Optional[StreamBody]:
        is_accepted = False
        total_delay = 0
        while is_accepted or (total_delay < timeout):
            r = self._get_request_accepted(stream_id)
            if r:
                is_accepted = True
                break
            await asyncio.sleep(delay)
            total_delay += delay
        # self._redis_client.xdel(self.request_key, r.stream_id)
        return r

    async def _wait_for_finish(self, stream_id: bytes, delay: int = 0.1, timeout=10) -> Optional[StreamBody]:
        is_arrived = False
        total_delay = 0
        while is_arrived or (total_delay < timeout):
            r = self._get_response_arrived(stream_id)
            if r:
                is_arrived = True
                break
            await asyncio.sleep(delay)
            total_delay += delay

        self._redis_client.xdel(self.response_key, r.stream_id)
        return r

    def _get_request_accepted(self, stream_id: bytes) -> Optional[bytes]:
        messages: List = self._redis_client.xpending_range(
            self.request_key,
            groupname=self.processor_group,
            count=1,
            min=stream_id,
            max=stream_id,
        )
        if messages:
            message = Message(**messages[0])
            pending_time = (message.time_since_delivered - message.times_delivered) / 1000
            return message.message_id
        else:
            return

    def _get_response_arrived(self, stream_id: bytes) -> Optional[StreamBody]:
        # messages: List = self._redis_client.xpending_range(
        #     self.response_key,
        #     groupname=self.batcher_group,
        #     count=1,
        #     min=stream_id,
        #     max=stream_id,
        # )
        messages: List = self._redis_client.xrange(
            self.response_key,
            min=stream_id,
            max=stream_id,
        )
        if messages:
            # message = Message(**messages[0])
            message = messages[0]
            _id, _body = message
            self._redis_client.xack(
                self.response_key,
                self.batcher_group,
                _id,
            )
            return StreamBody(_id, _body)
        else:
            return

    # async def _check_response_arrived(self, stream_id: bytes):
    #     # messages: List = self._redis_client.xreadgroup
    #     self._check_request_accepted(stream_id=stream_id)
    #     messages: List = self._redis_client.xrange(
    #         self.response_key,
    #         min=stream_id,
    #         max=stream_id,
    #     )
    #     if messages:
    #         return messages[0]
    #     else:
    #         return 


@logged
class BatchProcessor:
    def __init__(
            self,
            batch_time: int = 2,
            batch_size: int = 64,
            # host: str = "localhost",
            # port: int = 6379,
            # db: int = 0,
            # password: Optional[str] = None,
            # key="infer",
            # group="infergrp",
        ):
        # if not self.__log:
        #     import logging, sys
        #     logging.basicConfig(stream=sys.stdout)
        #     self.__log = logging.getLogger(self.__class__.__name__)
        #     self.__log.setLevel(os.getenv('LOG_LEVEL', logging.DEBUG))
        self.delay = 0.1
        self.batch_time = batch_time
        self.batch_size = batch_size
        self._redis_client = get_client(
            host=REDIS__HOST,
            port=REDIS__PORT,
            db=REDIS__DB,
            password=REDIS__PASSWORD,
        )
        self.request_key = REDIS__STREAM_KEY_REQUEST
        self.response_key = REDIS__STREAM_KEY_RESPONSE
        self.processor_group = REDIS__STREAM_GROUP_PROCESSOR
        self.batcher_group = REDIS__STREAM_GROUP_BATCHER

    async def start_daemon(self, func: Callable) -> None:
        self.__log.info(
            ' '.join([
                f'BatchProcessor start:',
                f'delay={self.delay},',
                f'batch_time={self.batch_time}',
                f'batch_size={self.batch_size}',
            ])
        )
        while True:
            asyncio.run(self.run(func))

        # loop.create_task(self.run(func))


        # while True:
        #     await asyncio.run(self.run(func))

    async def run(self, func: Callable) -> None:
        delay_period = 0
        batch_gathered = 0
        requests = []
        while delay_period < self.batch_time and batch_gathered < self.batch_size:
            # self.__log.debug(
            #     f'get_next_batch: {delay_period}/{self.batch_time}, {batch_gathered}/{self.batch_size}'
            # )
            # print(
            #     f'get_next_batch: {delay_period}/{self.batch_time}, {batch_gathered}/{self.batch_size}'
            # )
            new_request = await self.get_next_batch()
            if new_request:
                requests.extend(new_request)

            batch_gathered = len(requests)
            delay_period += self.delay

            await asyncio.sleep(self.delay)

        if requests:
            print(f'batch start: {delay_period}/{self.batch_time}, {batch_gathered}/{self.batch_size}')
            # self.__log.debug(f'batch start: {delay_period}/{self.batch_time}, {batch_gathered}/{self.batch_size}')
            streams = [v[0] for i, v in requests]
            streams = sorted(streams, key=lambda x: x[0], reverse=True)
            stream_ids = [i for i, v in streams]
            stream_bodies = [v for i, v in streams]

            try:
                results = func(stream_bodies)
            except Exception as e:
                self.__log.error(f'Error while running `{func.__name__}`: {e}')

            #TODO: 
            # Exception has occurred: ResponseError
            # The ID specified in XADD is equal or smaller than the target stream top item
            # File "/Users/a09255/git/dynamic_batcher/dynamic_batcher/batcher.py", line 282, in run
            #     self._redis_client.xadd(
            # File "/Users/a09255/git/dynamic_batcher/dynamic_batcher/__main__.py", line 23, in <module>
            #     asyncio.run(batch_processor.run(set_name))
            # redis.exceptions.ResponseError: The ID specified in XADD is equal or smaller than the target stream top item
            for stream_id, stream_body in zip(stream_ids, results):
                self._redis_client.xadd(
                    self.response_key,
                    # {'body': json.dumps(stream_body)},
                    stream_body,
                    stream_id,
                )
            self._redis_client.xack(self.request_key, self.processor_group, *stream_ids)
            self._redis_client.xdel(self.request_key, *stream_ids)

    
    async def get_next_batch(self) -> Optional[List]:

        try:
            requests: List = self._redis_client.xreadgroup(
                groupname=self.processor_group,
                consumername=self.processor_group,
                streams={self.request_key: '>'},
                # count=self.batch_size,
                count=1,
                block=self.batch_time,
                noack=False,
            )
            # self._redis_client.xreadgroup(
            #     groupname=self.processor_group,
            #     consumername='c',
            #     streams={self.request_key: 1},
            #     block=self.batch_time,
            #     noack=False,
            # )
            if requests:
                return requests
            else:
                return

        except Exception as e:
            self.__log.error(f'Error while reading message {e}')
