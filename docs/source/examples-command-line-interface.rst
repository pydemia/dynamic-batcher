=================================================
Command-line Interface
=================================================

:Release: |release|



Command-line Interface to launch `BatchProcessor`
=================================================

We provide the command-line interface to launch `BatchProcessor` easily.
You can only focus on using `DynamicBatcher` with this command.


    .. code-block:: bash

        $ dynamic_batch_processor 'module.submodule.callable' --batch-size=64 --batch-time=2 --log-level=INFO


Args
----

    callable (str):
        Callable name to execute. ex.: 'module.submodule.func'
    
    -bs/--batch-size (int):
        Batch size of BatchProcessor. Defaults to ``64``.
    
    -bt/--batch-time (int):
        Batch time delay(seconds) of BatchProcessor. Defaults to ``2``.
    
    -lv/--log-level (str):
        Log Level. Defaults to ``INFO``.

    -lf/--log-config-file (str):
        Log Config file path. Optional.
    
    -lj/--log-config-json (str):
        Log Config file(json) path. Optional.


Example
-------

    .. code-block:: python

        # example.py
        from typing import List, Dict
        def add_1(bodies: List[Dict]) -> List[Dict]:
            for body in bodies:
                int_list = body['nested']['values']
                body['nested']['result'] = list(map(lambda x: x+1, int_list))
            return bodies


    .. code-block:: bash

        $ ls  # The module `example.py` can be imported.
        example.py
        $ dynamic_batch_processor 'example.add_1' --batch-size=64 --batch-time=2
        [2023-12-18 18:47:02 +0900] [88396] [INFO] LOG_LEVEL: INFO
        [2023-12-18 18:47:02 +0900] [88396] [INFO] BatchProcessor start: delay=0.001, batch_size=64 batch_time=2

    .. code-block:: bash

        $ ls  # The module `example.py` can be imported.
        example.py
        $ dynamic_batch_processor 'example.add_1' --log-level=DEBUG --batch-size=64 --batch-time=2
        [2023-12-18 18:47:02 +0900] [88396] [INFO] LOG_LEVEL: DEBUG
        [2023-12-18 18:47:02 +0900] [88396] [INFO] BatchProcessor start: delay=0.001, batch_size=64 batch_time=2
        [2023-12-18 18:47:09 +0900] [88396] [DEBUG] Trimmed old requests: 0
        [2023-12-18 18:47:09 +0900] [88396] [DEBUG] Trimmed old responses: 0
