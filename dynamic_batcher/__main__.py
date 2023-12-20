"""
====================================
 :mod:`dynamic_batcher` Module
====================================
.. moduleauthor:: Youngju Jaden Kim <pydemia@gmail.com>
.. note:: Info

Info
====
    We provide the command-line interface to launch ``BatchProcessor`` easily.
    You can only focus on using ``DynamicBatcher`` and run ``BatchProcessor`` with this command.

Args
----

    callable (str):
        Callable name to execute. ex.: 'module.submodule.func'.
        The callable should have has only one positional argument that typed 'List'.
    
    -bs/--batch-size (int):
        Batch size of BatchProcessor. if it is not provided, use envvar ``DYNAMIC_BATCHER__BATCH_SIZE`` instead. Defaults to ``64``.
    
    -bt/--batch-time (int):
        Batch time delay(seconds) of BatchProcessor. if it is not provided, use envvar ``DYNAMIC_BATCHER__BATCH_TIME`` instead. Defaults to ``2``.
    
    -lf/--log-config-file (str):
        Log Config file path. Optional.
    
    -lj/--log-config-json (str):
        Log Config file(json) path. Optional.


Example
-------

    .. code-block:: python

        # example.py
        def add_1(bodies: List[Dict]) -> List[Dict]:
            for body in bodies:
                int_list = body['nested']['values']
                body['nested']['result'] = list(map(lambda x: x+1, int_list))
            return bodies


    .. code-block:: bash

        $ dynamic_batch_processor 'example.add_1' --batch-size=64 --batch-time=2 --log-config-file=logging.conf

"""

import argparse
import os
import asyncio

from .logger import Logger
from .validate import validate_callable

from dynamic_batcher import BatchProcessor


argparser = argparse.ArgumentParser(
    prog="dynamic-batcher",
    description="Dynamic Batcher CLI",
)

argparser.add_argument(
    "callable",
    type=str,
    help="Callable name to execute. ex.: 'module.submodule.func'"
)

argparser.add_argument(
    "-bs", "--batch-size",
    help="Batch size of BatchProcessor",
    type=int,
    default=int(os.getenv("DYNAMIC_BATCHER__BATCH_SIZE", "64")),
    required=False,
)
argparser.add_argument(
    "-bt", "--batch-time",
    help="Batch time delay of BatchProcessor",
    type=int,
    default=int(os.getenv("DYNAMIC_BATCHER__BATCH_TIME", "2")),
    required=False,
)

argparser.add_argument(
    "-lv", "--log-level",
    help="Log Level",
    type=str,
    default="INFO",
    required=False,
)
argparser.add_argument(
    "-lf", "--log-config-file",
    help="Log Config file path",
    type=str,
    default=None,
    required=False,
)
argparser.add_argument(
    "-lj", "--log-config-json",
    help="Log Config file(json) path",
    type=str,
    default=None,
    required=False,
)


def run_batch_processor():
    args, _ = argparser.parse_known_args()

    batch_callable = validate_callable(-1)(args.callable)

    logger = Logger(
        level=args.log_level,
        log_config_file=args.log_config_file,
        log_config_json=args.log_config_json,
    )

    batch_processor = BatchProcessor(
        batch_size=args.batch_size,
        batch_time=args.batch_time,
    )
    asyncio.run(batch_processor.start_daemon(batch_callable))



if __name__ == '__main__':
    run_batch_processor()
