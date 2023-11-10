import redis

# r = redis.Redis(host='localhost', port=6379, db=0)
r = redis.Redis(host='localhost', port=6379, db=0, protocol=3)
r.set('foo', 'bar')

r.get('foo')


# # Redis Pipeline
# pipe = r.pipeline()
# pipe.set('foo', 5)
# pipe.set('bar', 18.5)
# pipe.set('blee', "hello world!")
# pipe.execute()
# [True, True, True]

# # Redis Pub/Sub
# r = redis.Redis(...)
# p = r.pubsub()
# p.subscribe('my-first-channel', 'my-second-channel', ...)
# p.get_message()
# {'pattern': None, 'type': 'subscribe', 'channel': b'my-second-channel', 'data': 1}

# # Redis Stream
# redis_host = "redis"
# stream_key = "skey"
# stream2_key = "s2key"
# group1 = "grp1"
# group2 = "grp2"

import redis
from time import time
from redis.exceptions import ConnectionError, DataError, NoScriptError, RedisError, ResponseError

r = redis.Redis(host='localhost', port=6379, db=0, protocol=3, password='corus!')
r.ping()

key = 'INPUT'

for i in range(0,100):
    r.xadd(key, { 'ts': time(), 'v': i } )

print(f"stream length: {r.xlen(key)}")


l = r.xread( count=2, streams={key: 0} )
print(l)

# wait for 5s for new messages
BATCH_SIZE = 100
seconds = 1000
TIMEOUT = 2*seconds
l = r.xread( count=BATCH_SIZE, block=TIMEOUT, streams={key: '$'} )
print( f"after 2s TIMEOUT, got an empty list {l}, no *new* messages on the stream")
print( f"stream length: {r.xlen(key)}")

