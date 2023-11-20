====================================
Quickstart
====================================

:Release: |release|


* :ref:`gathering-api-requests-as-one-batch`

.. _gathering-api-requests-as-one-batch:

Gathering API requests as one batch
====================================

First, run a redis server:

::

    $ docker run --rm -p 6379:6379 -e ALLOW_EMPTY_PASSWORD=yes bitnami/redis:latest
    redis 00:02:54.05 
    redis 00:02:54.06 Welcome to the Bitnami redis container
    redis 00:02:54.06 Subscribe to project updates by watching https://github.com/bitnami/containers
    redis 00:02:54.06 Submit issues and feature requests at https://github.com/bitnami/containers/issues
    redis 00:02:54.06 
    redis 00:02:54.07 INFO  ==> ** Starting Redis setup **
    redis 00:02:54.08 WARN  ==> You set the environment variable ALLOW_EMPTY_PASSWORD=yes. For safety reasons, do not use this flag in a production environment.
    redis 00:02:54.09 INFO  ==> Initializing Redis
    redis 00:02:54.11 INFO  ==> Setting Redis config file
    redis 00:02:54.15 INFO  ==> ** Redis setup finished! **

    redis 00:02:54.16 INFO  ==> ** Starting Redis **
    1:C 20 Nov 2023 00:02:54.189 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
    1:C 20 Nov 2023 00:02:54.189 # Redis version=7.0.12, bits=64, commit=00000000, modified=0, pid=1, just started
    1:C 20 Nov 2023 00:02:54.189 # Configuration loaded
    1:M 20 Nov 2023 00:02:54.189 * monotonic clock: POSIX clock_gettime
    1:M 20 Nov 2023 00:02:54.191 * Running mode=standalone, port=6379.
    1:M 20 Nov 2023 00:02:54.191 # Server initialized
    1:M 20 Nov 2023 00:02:54.197 * Creating AOF base file appendonly.aof.1.base.rdb on server start
    1:M 20 Nov 2023 00:02:54.200 * Creating AOF incr file appendonly.aof.1.incr.aof on server start
    1:M 20 Nov 2023 00:02:54.200 * Ready to accept connections

Create an app with ``DynamicBatcher``:

::

    # app.py

    import time
    import uvicorn
    from typing import List
    from fastapi import FastAPI
    from pydantic import BaseModel
    from dynamic_batcher import DynamicBatcher

    app = FastAPI()
    batcher = DynamicBatcher()

    class RequestItem(BaseModel):
        values: List[int] = [1, 5, 2]

    @app.post("/batch/{key}")
    async def run_batch(key: str, body: RequestItem):
        start_time = time.time()
        resp_body = await batcher.asend(body.model_dump())
        result = {
            "key": key,
            "values": body.values,
            "values_sum": resp_body,
            "elapsed": time.time() - start_time
        }
        return result

    if __name__ == "__main__":
        uvicorn.run(app)

::

    INFO:     Started server process [27085]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)


Create a ``BatchProcessor``:

::

    # process.py

    ## process_fn
    import asyncio
    from dynamic_batcher import BatchProcessor
    from typing import List, Dict
    body_list = [
        {'values': [1, 2, 3]},
        {'values': [4, 5, 6]}
    ]
    def sum_values(bodies: List[Dict]) -> List[Dict]:
        result = []
        for body in bodies:
            result.append( { 'sum': sum(body['values']) } )
        return result

    # sum_values(body_list) -> [{'sum': 6}, {'sum': 15}]

    batch_processor = BatchProcessor(batch_size=5, batch_time=2)
    asyncio.run(batch_processor.start_daemon(sum_values))


Create a request:

::

    $ curl -X POST localhost:8000/batch/single \
        -H 'Content-Type: application/json' \
        -d '{"key": "a", "values": [1, 3, 5]}'
    {"key":"single","values":[1,3,5],"values_sum":{"sum":9},"elapsed":2.470838212966919}

Create requests simultaneously:

::

    $ seq 1 17 | xargs -n1 -I {} -P20 curl -w "\n" -X POST localhost:8000/batch/{} \
        -H 'Content-Type: application/json' \
        -d '{"key": "a", "values": [1, 3, 5]}'
    {"key":"2","values":[1,3,5],"values_sum":{"sum":9},"elapsed":0.026194095611572266}
    {"key":"1","values":[1,3,5],"values_sum":{"sum":9},"elapsed":0.02919602394104004}
    {"key":"4","values":[1,3,5],"values_sum":{"sum":9},"elapsed":0.03496694564819336}
    {"key":"3","values":[1,3,5],"values_sum":{"sum":9},"elapsed":0.03712725639343262}
    {"key":"5","values":[1,3,5],"values_sum":{"sum":9},"elapsed":0.03885698318481445}
    {"key":"6","values":[1,3,5],"values_sum":{"sum":9},"elapsed":0.07140994071960449}
    {"key":"7","values":[1,3,5],"values_sum":{"sum":9},"elapsed":0.07084202766418457}
    {"key":"8","values":[1,3,5],"values_sum":{"sum":9},"elapsed":0.03500699996948242}
    {"key":"9","values":[1,3,5],"values_sum":{"sum":9},"elapsed":0.03584885597229004}
    {"key":"10","values":[1,3,5],"values_sum":{"sum":9},"elapsed":0.03512001037597656}
    {"key":"11","values":[1,3,5],"values_sum":{"sum":9},"elapsed":0.03521585464477539}
    {"key":"13","values":[1,3,5],"values_sum":{"sum":9},"elapsed":0.03747105598449707}
    {"key":"12","values":[1,3,5],"values_sum":{"sum":9},"elapsed":0.0377802848815918}
    {"key":"14","values":[1,3,5],"values_sum":{"sum":9},"elapsed":0.03834390640258789}
    {"key":"16","values":[1,3,5],"values_sum":{"sum":9},"elapsed":0.039556026458740234}
    {"key":"15","values":[1,3,5],"values_sum":{"sum":9},"elapsed":3.737711191177368}
    {"key":"17","values":[1,3,5],"values_sum":{"sum":9},"elapsed":3.739470720291138}

The remainder(2) was delayed until ``batch_time`` is up.