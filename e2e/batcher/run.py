from typing import List, Dict
import os
import sys
import uuid
import asyncio
import logging
import logging.config
from pathlib import Path


logging.config.fileConfig(
    Path(__file__).parent.absolute().joinpath('logging.conf'),
)

from dynamic_batcher import DynamicBatcher, BatchProcessor

DYNAMIC_BATCHER__BATCH_SIZE = int(os.getenv("DYNAMIC_BATCHER__BATCH_SIZE", "64"))
DYNAMIC_BATCHER__BATCH_TIME = int(os.getenv("DYNAMIC_BATCHER__BATCH_TIME", "2"))


def add_1(bodies: List[Dict]) -> List[Dict]:
    for body in bodies:
        body['name'] = f'{uuid.uuid4()}'
        int_list = body['nested']['values']
        body['nested']['values_add1'] = list(map(lambda x: x+1, int_list))

    return bodies


if __name__ == '__main__':
    log = logging.getLogger()
    log.info('start test daemon')
    batcher = DynamicBatcher()
    batch_processor = BatchProcessor(
        batch_size=DYNAMIC_BATCHER__BATCH_SIZE,
        batch_time=DYNAMIC_BATCHER__BATCH_TIME,
    )

    asyncio.run(batch_processor.start_daemon(add_1))
