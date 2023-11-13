from typing import Optional, List, Dict
import asyncio
import uuid
import random
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import RedirectResponse

from dynamic_batcher import DynamicBatcher


def set_name(bodies: List[Dict]) -> List[Dict]:
    for body in bodies:
        body['name'] = f'{uuid.uuid4()}'

    return bodies

from contextlib import asynccontextmanager
from dynamic_batcher import BatchProcessor

# batch_processor = BatchProcessor(batch_size=64, batch_time=10)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # batch_processor.start_daemon(set_name)
#     while True:
#         asyncio.run(batch_processor.run(set_name))

# loop = asyncio.get_event_loop()
# loop.create_task(batch_processor.start_daemon(set_name))
# loop.run_forever()
# while True:
#     asyncio.run(batch_processor.run(set_name))
# batch_processor.start_daemon(set_name)


# asyncio.run(batch_processor.start_daemon(set_name))

# app = FastAPI(lifespan=lifespan)
app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ]
        }
    }

@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url='/docs')


@app.post("/items/")
async def create_item(item: Item):
    return item


@app.get("/items/{item_id}")
async def read_item(
        item_id,
        delay: Optional[int] = None,
    ):
    if delay:
        delay = random.randint(0, delay - 1) + random.random()
        await asyncio.sleep(delay)

    result = {
        "item_id": item_id,
        "delay": delay,
    }
    return result


class RequestItem(BaseModel):
    content: str


@app.post("/items/{item_id}")
async def infer_item(
        body: RequestItem,
        delay: Optional[int] = None,
    ):
    if delay:
        delay = random.randint(0, delay - 1) + random.random()
        await asyncio.sleep(delay)

    batcher = DynamicBatcher()
    resp = await batcher.asend(body.model_dump())
    result = {
        "item_id": resp.body,
        "delay": delay,
    }
    return result


@app.post("/items/test/{item_id}")
async def infer_test_item(
        body: RequestItem,
        delay: Optional[int] = None,
    ):
    if delay:
        delay = random.randint(0, delay - 1) + random.random()
        await asyncio.sleep(delay)

    batcher = DynamicBatcher()
    resp = await batcher.asend(body.model_dump())
    result = {
        "item_id": resp.body,
        "delay": delay,
    }
    return result


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    result = {"item_id": item_id, "item": item}
    return result
