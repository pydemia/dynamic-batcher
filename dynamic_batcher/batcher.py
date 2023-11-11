from typing import Optional, Dict
import os
import redis
import asyncio
from redis.exceptions import (
    ConnectionError,
    DataError,
    NoScriptError,
    RedisError,
    ResponseError,
)


__all__ = [
    "DynamicBatcher",
]


REDIS__HOST = os.getenv("REDIS__HOST", "localhost")
REDIS__PORT = int(os.getenv("REDIS__PORT", "6379"))
REDIS__DB = int(os.getenv("REDIS__DB", "0"))
REDIS__PASSWORD = os.getenv("REDIS__PASSWORD", None)
REDIS__STREAM_KEY = os.getenv("REDIS__STREAM_KEY", "skey")
REDIS__STREAM_GROUP = os.getenv("REDIS__STREAM_GROUP", "sgroup")


_REDIS_CLIENT = redis.Redis(
    host=REDIS__HOST,
    port=REDIS__PORT,
    db=REDIS__DB,
    password=REDIS__PASSWORD,
)
if not _REDIS_CLIENT.ping():
    raise ConnectionError(
        f"Unable to connect Redis server: {REDIS__HOST}:{REDIS__PORT}"
    )
try:
    _REDIS_CLIENT.xgroup_create(
        name=REDIS__STREAM_KEY,
        groupname=REDIS__STREAM_GROUP,
        # id=0,
    )
except ResponseError as e:
    print(f"raised: {e}")


class DynamicBatcher:
    def __init__(
            self,
            # host: str = "localhost",
            # port: int = 6379,
            # db: int = 0,
            # password: Optional[str] = None,
            # key="infer",
            # group="infergrp",
        ):
        self._redis_client = _REDIS_CLIENT

    def set_key_value(self, key: str, value) -> bool:
        return self._redis_client.set(key=key,value=value)
    
    async def asend(self, body: Dict, *args, **kwargs):
        requested = self._redis_client.xadd(REDIS__STREAM_KEY, body)

        # return await self._redis_client.execute_command(*args, **kwargs)

class BatchBroker:
    def __init__(
            self,
            # host: str = "localhost",
            # port: int = 6379,
            # db: int = 0,
            # password: Optional[str] = None,
            # key="infer",
            # group="infergrp",
        ):
        self._redis_client = _REDIS_CLIENT

    async def get_next_batch(self, consumer_name: str):
        try:
            response = self._redis_client.xreadgroup(
                groupname=REDIS__STREAM_GROUP,
                consumername=consumer_name,
                streams={REDIS__STREAM_KEY: ">"},  # Read from the latest
            )
            
            if not response:
                return None

            stream_id, messages = response[0]
        
        except Exception as e:
            print(f"Error while reading message {e}")
            
        else:

            ids_and_messages = [(message["id"], message) for _, message in messages]

            last_message_id_in_group_stream_map_response = max([int(id.decode()) for id,_ in ids_and_messages])
            
            await asyncio.sleep(1)
            
        finally:

            pass
