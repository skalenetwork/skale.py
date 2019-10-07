#!/usr/bin/env bash

set -e

CURRENT_VERSION="$(python setup.py --version)"
sed -i "s/${CURRENT_VERSION}/${VERSION}/g" setup.py

rm -rf ./dist/*

python setup.py sdist
python setup.py bdist_wheel

echo "==================================================================="
echo "Done build: skale.py $VERSION/"

