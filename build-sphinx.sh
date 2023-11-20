#!/usr/bin/env bash

# sphinx-quickstart docs
# sphinx-build -M html docs/source docs/build

sphinx-apidoc -f -o docs/source dynamic_batcher \
    --separate \
    --module-first \
    -d 5 \
    -H dynamic_batcher

cd docs && make html