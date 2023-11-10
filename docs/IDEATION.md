# Ideation

# Requirements

# Items
* Request Queue
* Timeout
* Batch Size
* 


# Psuedo Code

```py
* 
TIMEOUT=2
BATCH_SIZE=64

queue = []

condition_is_met = False
while condition_is_met:
  queue.insert(request)
  if wait_time == TIMEOUT | len(queue) == BATCH_SIZE:
    return inference(queue)
  
```

---

* broker

```py
class Broker:
    async def request_waitable(request, request_id):
        redis.lpush((request_id, request))

        await fut = redis.get(request_id)
        while redis.get(request_id).status != 'Done':
            fut = redis.get(request_id)
        return fut

    async def 
```


```py

```


* client

```py
def client(request):
    request_id = uuid.uuid4()
    

```
