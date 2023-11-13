from .batcher import DynamicBatcher, BatchProcessor


import asyncio

batcher = DynamicBatcher()
batch_processor = BatchProcessor(batch_time=2, batch_size=64)

from typing import List, Dict
import uuid
def set_name(bodies: List[Dict]) -> List[Dict]:
    for body in bodies:
        body['name'] = f'{uuid.uuid4()}'

    return bodies


# async def start_daemon()

if __name__ == '__main__':
    # r = batch_processor.start_daemon(set_name)
    while True:
        asyncio.run(batch_processor.run(set_name))
