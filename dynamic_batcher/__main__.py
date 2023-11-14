from .batcher import DynamicBatcher, BatchProcessor
import logging
import sys

logging.basicConfig(
    stream=sys.stdout,
)



# import os
# import asyncio


# DYNAMIC_BATCHER__BATCH_SIZE = int(os.getenv("DYNAMIC_BATCHER__BATCH_SIZE", "64"))
# DYNAMIC_BATCHER__BATCH_TIME = int(os.getenv("DYNAMIC_BATCHER__BATCH_TIME", "2"))

# batcher = DynamicBatcher()
# batch_processor = BatchProcessor(
#     batch_size=DYNAMIC_BATCHER__BATCH_SIZE,
#     batch_time=DYNAMIC_BATCHER__BATCH_TIME,
# )




# from typing import List, Dict
# import uuid
# def set_name(bodies: List[Dict]) -> List[Dict]:
#     for body in bodies:
#         body['name'] = f'{uuid.uuid4()}'

#     return bodies


# # async def start_daemon()

# if __name__ == '__main__':
#     asyncio.run(batch_processor.start_daemon(set_name))
#         # asyncio.run(batch_processor.run(set_name))
