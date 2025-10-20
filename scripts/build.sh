#!/usr/bin/env bash

set -e

sed -i "s/version = \".*\"/version = \"${VERSION}\"/g" pyproject.toml

rm -rf ./dist/*

uv build

echo "==================================================================="
echo "Done build: skale.py $VERSION/"

