import json
import pytest
import redis
from dynamic_batcher import ResponseStream
from dynamic_batcher import redis_engine


def test_get_client():
    client = redis_engine.get_client(
        host=redis_engine.REDIS__HOST,
        port=redis_engine.REDIS__PORT,
        db=redis_engine.REDIS__DB,
        password=redis_engine.REDIS__PASSWORD,
    )
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

def test_redis_get_default_client():
    client = redis_engine.get_default_client()
    assert client.ping()

    assert client.xinfo_stream(redis_engine.REDIS__STREAM_KEY_REQUEST)
    assert client.xinfo_stream(redis_engine.REDIS__STREAM_KEY_RESPONSE)

    request_group_info = client.xinfo_groups(redis_engine.REDIS__STREAM_KEY_REQUEST)
    response_group_info = client.xinfo_groups(redis_engine.REDIS__STREAM_KEY_RESPONSE)
    
    # [{'name': 'processor', 'consumers': 0, 'pending': 0, 'last-delivered-id': '0-0', 'entries-read': None, 'lag': 0}]
    assert redis_engine.REDIS__STREAM_GROUP_PROCESSOR in [grp['name'] for grp in request_group_info]
    assert redis_engine.REDIS__STREAM_GROUP_BATCHER in [grp['name'] for grp in response_group_info]

    body = {
        "name": "test",
        "data": {
            "content": "xxx",
        },
    }
    try:
        stream_id = client.xadd(
            redis_engine.REDIS__STREAM_KEY_REQUEST,
            json.dumps(body),
        )
        raise TypeError('Check dict support failed.')
    except Exception as e:
        assert isinstance(e, redis.exceptions.DataError)

    stream_id = client.xadd(redis_engine.REDIS__STREAM_KEY_REQUEST, {"body": json.dumps(body)})
    streams = client.xreadgroup(
        redis_engine.REDIS__STREAM_GROUP_PROCESSOR,
        consumername=redis_engine.REDIS__STREAM_GROUP_PROCESSOR,
        streams={redis_engine.REDIS__STREAM_KEY_REQUEST: '>'},
        count=1,
        # block=self.batch_time,
        noack=False,
    )
    stream = [v[0] for i, v in streams][0]
    _id, _fields = stream
    _body = _fields['body']
    assert isinstance(_id, str) and _id == stream_id
    assert isinstance(_body, str) and _body == json.dumps(body)
