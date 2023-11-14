from typing import Optional, List, Dict
import os
import time
import uuid
import random
import asyncio
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from fastapi.responses import RedirectResponse

from dynamic_batcher import DynamicBatcher


def get_dynamic_batcher():
    return DynamicBatcher(delay=0.01, timeout=100)


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
        batcher: DynamicBatcher = Depends(get_dynamic_batcher),
    ):
    if delay:
        delay = random.randint(0, delay - 1) + random.random()
        await asyncio.sleep(delay)

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
        batcher: DynamicBatcher = Depends(get_dynamic_batcher),
    ):
    start_t = time.time()
    if delay:
        delay = random.randint(0, delay - 1) + random.random()
        await asyncio.sleep(delay)

    resp_body = await batcher.asend(body.model_dump())
    result = {
        "data": resp_body,
        "elapsed_time": time.time() - start_t,
    }
    return result


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    result = {"item_id": item_id, "item": item}
    return result
