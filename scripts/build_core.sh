#!/usr/bin/env bash

set -e

VERSION=$(grep '^version = ' packages/skale-core/pyproject.toml | cut -d'"' -f2)

rm -rf packages/skale-core/dist/*

uv build --package skale-py-core --out-dir packages/skale-core/dist

echo "==================================================================="
echo "Done build: skale.py-core $VERSION/"
