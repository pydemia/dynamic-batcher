====================================
Quickstart
====================================

:Release: |release|



Command-line Interface to launch `BatchProcessor`
=================================================

We provide the command-line interface to launch `BatchProcessor` easily.
You can only focus on using `DynamicBatcher` with this command.


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
        def add_1(bodies: List[Dict]) -> List[Dict]:
            for body in bodies:
                int_list = body['nested']['values']
                body['nested']['result'] = list(map(lambda x: x+1, int_list))
            return bodies


    .. code-block:: bash

        $ python -m dynamic_batcher 'example.add_1' --batch-size=64 --batch-time=2
        [2023-12-18 16:35:46 +0900] [74985] [INFO] BatchProcessor start: delay=0.001, batch_size=64 batch_time=2

    .. code-block:: bash

        $ python -m dynamic_batcher 'example.add_1' --log-level=DEBUG --batch-size=64 --batch-time=2
        [2023-12-18 16:35:46 +0900] [74985] [INFO] BatchProcessor start: delay=0.001, batch_size=64 batch_time=2
