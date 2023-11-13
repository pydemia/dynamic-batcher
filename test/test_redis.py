import pytest
from dynamic_batcher import redis_engine
import json


def test_get_client():
    client = redis_engine.get_client(
        host=redis_engine.REDIS__HOST,
        port=redis_engine.REDIS__PORT,
        db=redis_engine.REDIS__DB,
        password=redis_engine.REDIS__PASSWORD,
    )
    assert client.ping()

def test_get_default_client():
    client = redis_engine.get_default_client()
    assert client.ping()

# def test_ping_redis():
#     # assert redis.ping()
#     return True


# @pytest.fixture
# def shutdown_redis():
#     assert redis.launch()
#     assert redis.shutdown()
#     return True


# @pytest.fixture
# def restart_redis():
#     assert redis.launch()
#     assert redis.restart()
#     return True


# @pytest.fixture
def test_info_redis():
    return redis_engine.info()


####################################################

def test_redis_add_read():
    client = redis_engine.get_default_client()
    body = {
        "name": "test",
        "data": {
            "content": "xxx",
        },
    }
    
    body_json = json.dumps(body)
    r = client.xadd(redis_engine.REDIS__STREAM_KEY, {"body": body_json})

    l = client.xread(count=1, streams={redis_engine.REDIS__STREAM_KEY: 10})
    client.xread(streams={redis_engine.REDIS__STREAM_KEY: r})
    client.xrange(redis_engine.REDIS__STREAM_KEY, min=r, max=r)
    client.xreadgroup(
        groupname=redis_engine.REDIS__STREAM_GROUP,
        consumername="consumer",
        streams={redis_engine.REDIS__STREAM_KEY: ">"},
        count=2,
        block=2,
        noack=False,
    )
    # client.xpending(redis.REDIS__STREAM_KEY, groupname=redis.REDIS__STREAM_GROUP)
    client.xpending_range(redis_engine.REDIS__STREAM_KEY, groupname=redis_engine.REDIS__STREAM_GROUP, count=1, min=r, max=r)
    client.xack(redis_engine.REDIS__STREAM_KEY, redis_engine.REDIS__STREAM_GROUP, r)
    client.xadd('finished', {"body": json.dumps({"content": "done"})}, id=r)
    client.xpending_range(redis_engine.REDIS__STREAM_KEY, groupname=redis_engine.REDIS__STREAM_GROUP, count=1, min=r, max=r)

    client.s
    # client.xreadgroup(
    #     redis.REDIS__STREAM_GROUP,
    # )