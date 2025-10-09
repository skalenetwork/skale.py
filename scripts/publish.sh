#!/usr/bin/env bash

: "${PIP_USERNAME?Need to set PIP_USERNAME}"
: "${PIP_PASSWORD?Need to set PIP_PASSWORD}"

set -e

if [ "$TEST" = 1 ]; then
    uv publish --publish-url https://test.pypi.org/legacy/ dist/*
else
    echo "Uploading to pypi"
    uv publish --username $PIP_USERNAME --password $PIP_PASSWORD dist/*
fi

echo "==================================================================="
echo "Uploaded to pypi, check at https://pypi.org/project/skale.py/$VERSION/"
