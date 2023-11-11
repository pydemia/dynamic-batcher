from typing import Optional
import asyncio
import random
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import RedirectResponse

from dynamic_batcher import DynamicBatcher


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
    resp = batcher.asend(body)

    result = {
        "item_id": resp,
        "delay": delay,
    }
    return result


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    result = {"item_id": item_id, "item": item}
    return result
