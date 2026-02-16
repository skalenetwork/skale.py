#!/usr/bin/env bash

set -e

VERSION=${VERSION:-$(grep '^version = ' pyproject.toml | cut -d'"' -f2)}

sed -i "s/version = \".*\"/version = \"${VERSION}\"/g" packages/skale-core/pyproject.toml

rm -rf packages/skale-core/dist/*

uv build --package skale-py-core --out-dir packages/skale-core/dist

echo "==================================================================="
echo "Done build: skale.py-core $VERSION/"
