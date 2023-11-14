from typing import Optional
import os
import redis
from autologging import logged


__all__ = [
    "REDIS__HOST",
    "REDIS__PORT",
    "REDIS__DB",
    "REDIS__PASSWORD",
    "REDIS__STREAM_KEY_REQUEST",
    "REDIS__STREAM_GROUP_PROCESSOR",
    "REDIS__STREAM_KEY_RESPONSE",
    "REDIS__STREAM_GROUP_BATCHER",
    # "launch",
    # "ping",
    # "shutdown",
    # "restart",
    "info",
    "get_client",
    "get_default_client",
]


REDIS__HOST = os.getenv("REDIS__HOST", "localhost")
REDIS__PORT = int(os.getenv("REDIS__PORT", "6379"))
REDIS__DB = int(os.getenv("REDIS__DB", "0"))
REDIS__PASSWORD = os.getenv("REDIS__PASSWORD", None)
REDIS__STREAM_KEY_REQUEST = os.getenv("REDIS__STREAM_KEY_REQUEST", "request")
REDIS__STREAM_GROUP_PROCESSOR = os.getenv("REDIS__STREAM_GROUP_PROCESSOR", "processor")

REDIS__STREAM_KEY_RESPONSE = os.getenv("REDIS__STREAM_KEY_RESPONSE", "response")
REDIS__STREAM_GROUP_BATCHER = os.getenv("REDIS__STREAM_GROUP_BATCHER", "batcher")


def info():
    return {
        "REDIS__HOST": REDIS__HOST,
        "REDIS__PORT": REDIS__PORT,
        "REDIS__DB: ": REDIS__DB,
        "REDIS__STREAM_KEY_REQUEST": REDIS__STREAM_KEY_REQUEST,
        "REDIS__STREAM_GROUP_PROCESSOR": REDIS__STREAM_GROUP_PROCESSOR,
        "REDIS__STREAM_KEY_RESPONSE": REDIS__STREAM_KEY_RESPONSE,
        "REDIS__STREAM_GROUP_BATCHER": REDIS__STREAM_GROUP_BATCHER,
    }


@logged
def get_client(
        *args,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        # key: str = "infer",
        # group: str = "infergrp",
        **kwargs,
    ) -> redis.Redis:
    redis_client = redis.Redis(
        *args,
        host=host,
        port=port,
        db=db,
        password=password,
        decode_responses=True,
        **kwargs,
    )
    if not redis_client.ping():
        raise ConnectionError(
            f"Unable to connect Redis server: {REDIS__HOST}:{REDIS__PORT}"
        )


    # r = redis_client.xadd(REDIS__STREAM_KEY_REQUEST, {"body": 0})
    # redis_client.xdel(REDIS__STREAM_KEY_REQUEST, r)

    # r = redis_client.xadd(REDIS__STREAM_KEY_RESPONSE, {"body": 0})
    # redis_client.xdel(REDIS__STREAM_KEY_RESPONSE, r)

    try:
        redis_client.xgroup_create(
            name=REDIS__STREAM_KEY_REQUEST,
            groupname=REDIS__STREAM_GROUP_PROCESSOR,
            # id=0,
            mkstream=True,
        )
    except redis.ResponseError as e:
        pass

    try:
        redis_client.xgroup_create(
            name=REDIS__STREAM_KEY_RESPONSE,
            groupname=REDIS__STREAM_GROUP_BATCHER,
            # id=0,
            mkstream=True,
        )
    except redis.ResponseError as e:
        pass
    
    return redis_client


def get_default_client():
    return get_client(
        host=REDIS__HOST,
        port=REDIS__PORT,
        db=REDIS__DB,
        password=REDIS__PASSWORD,
    )
