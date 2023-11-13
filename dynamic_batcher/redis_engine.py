from typing import Optional
import os
import redis
import subprocess
from autologging import logged


__all__ = [
    "USE_LOCAL_REDIS",
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


USE_LOCAL_REDIS = os.getenv("USE_LOCAL_REDIS", "True")
REDIS__HOST = os.getenv("REDIS__HOST", "localhost")
REDIS__PORT = int(os.getenv("REDIS__PORT", "6379"))
REDIS__DB = int(os.getenv("REDIS__DB", "0"))
REDIS__PASSWORD = os.getenv("REDIS__PASSWORD", "redis!")
REDIS__STREAM_KEY_REQUEST = os.getenv("REDIS__STREAM_KEY_REQUEST", "request")
REDIS__STREAM_GROUP_PROCESSOR = os.getenv("REDIS__STREAM_GROUP_PROCESSOR", "processor")

REDIS__STREAM_KEY_RESPONSE = os.getenv("REDIS__STREAM_KEY_RESPONSE", "response")
REDIS__STREAM_GROUP_BATCHER = os.getenv("REDIS__STREAM_GROUP_BATCHER", "batcher")


# def launch() -> bool:
#     if bool(USE_LOCAL_REDIS):
#         # with open(os.devnull, 'w', encoding='utf-8') as devnull:
#         p = subprocess.Popen(
#             [
#                 "redis-server",
#                 "--port",
#                 f"{REDIS__PORT}",
#                 "--replicaof",
#                 f"{REDIS__HOST}",
#                 f"{REDIS__PORT}",
#                 "--requirepass",
#                 f"{REDIS__PASSWORD}"
#             ],
#             shell=False,
#             # stdout=devnull,
#             # stderr=devnull,
#         )
#         return ping()

# def _ping() -> bool:
#     try:
#         if redis.Redis(host=REDIS__HOST, port=REDIS__PORT, db=REDIS__DB).ping():
#             print("Redis launched successfully!")
#             return True
#         else:
#             raise ConnectionError("Redis cannot launched.")

#     except Exception as e:
#         raise ConnectionError("Redis cannot launched.") from e


# def ping() -> bool:
#     try:
#         return ping()
#     except Exception as e:
#         print(e)
#         return False


# def shutdown() -> bool:
#     if bool(USE_LOCAL_REDIS):
#         subprocess.call([
#             "redis-cli",
#             "-p",
#             f"{REDIS__PORT}",
#             "shutdown",
#         ])
#         return not ping()


# def restart() -> bool:
#     return shutdown() and launch()

def info():
    return {
        "USE_LOCAL_REDIS": USE_LOCAL_REDIS,
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


    r = redis_client.xadd(REDIS__STREAM_KEY_REQUEST, {"body": 0})
    redis_client.xdel(REDIS__STREAM_KEY_REQUEST, r)

    r = redis_client.xadd(REDIS__STREAM_KEY_RESPONSE, {"body": 0})
    redis_client.xdel(REDIS__STREAM_KEY_RESPONSE, r)

    try:
        redis_client.xgroup_create(
            name=REDIS__STREAM_KEY_REQUEST,
            groupname=REDIS__STREAM_GROUP_PROCESSOR,
            # id=0,
            # mkstream=True,
        )
    except redis.ResponseError as e:
        pass

    try:
        redis_client.xgroup_create(
            name=REDIS__STREAM_KEY_RESPONSE,
            groupname=REDIS__STREAM_GROUP_BATCHER,
            # id=0,
            # mkstream=True,
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
