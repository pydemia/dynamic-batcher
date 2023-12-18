from typing import List, Dict
import os
import sys
import asyncio
import logging
import logging.config
from pathlib import Path


# logging.config.fileConfig(
#     Path(__file__).parent.absolute().joinpath('logging.conf'),
# )

from dynamic_batcher import BatchProcessor

DYNAMIC_BATCHER__BATCH_SIZE = int(os.getenv("DYNAMIC_BATCHER__BATCH_SIZE", "64"))
DYNAMIC_BATCHER__BATCH_TIME = int(os.getenv("DYNAMIC_BATCHER__BATCH_TIME", "2"))


def add_1(bodies: List[Dict]) -> List[Dict]:
    for body in bodies:
        int_list = body['nested']['values']
        body['nested']['result'] = list(map(lambda x: x+1, int_list))

    return bodies


if __name__ == '__main__':
    # log = logging.getLogger()
    batch_processor = BatchProcessor()

    asyncio.run(batch_processor.start_daemon(add_1))
