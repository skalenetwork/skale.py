#!/usr/bin/env bash

: "${PIP_USERNAME?Need to set PIP_USERNAME}"
: "${PIP_PASSWORD?Need to set PIP_PASSWORD}"

set -e

if [ "$TEST" = 1 ]; then
    uv publish --publish-url https://test.pypi.org/legacy/ packages/skale-core/dist/*
else
    echo "Uploading skale.py-core to pypi"
    uv publish --username "$PIP_USERNAME" --password "$PIP_PASSWORD" packages/skale-core/dist/*
fi

VERSION=$(grep '^version = ' packages/skale-core/pyproject.toml | cut -d'"' -f2)
echo "==================================================================="
echo "Uploaded to pypi, check at https://pypi.org/project/skale.py-core/$VERSION/"
