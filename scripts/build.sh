#!/usr/bin/env bash

set -e

sed -i "s/^version = \".*\"/version = \"${VERSION}\"/" pyproject.toml
sed -i "s/^\( *\)\"skale\.py-core\",$/\1\"skale.py-core==${VERSION}\",/" pyproject.toml

rm -rf ./dist/*

uv build

echo "==================================================================="
echo "Done build: skale.py $VERSION/"

