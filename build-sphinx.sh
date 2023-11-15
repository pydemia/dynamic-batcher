#!/usr/bin/env bash

# sphinx-quickstart docs
# sphinx-build -M html docs/source docs/build

sphinx-apidoc -f -o docs/source dynamic_batcher

cd docs && make html