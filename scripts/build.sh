#!/usr/bin/env bash

set -e

bumpversion --allow-dirty --new-version $VERSION setup.py

rm -rf ./dist/*

python setup.py sdist
python setup.py bdist_wheel

echo "==================================================================="
echo "Done build: skale.py $VERSION/"

