#!/usr/bin/env bash

set -e
#set -x

NOT_VALID_BUMP_LEVEL_TEXT="Please provide bump level: major/minor/patch"
CURRENT_VERSION="$(python setup.py --version)"

if [ -z "$1" ]
then
    (>&2 echo $NOT_VALID_BUMP_LEVEL_TEXT)
    exit 1
else
    echo "Bumping $CURRENT_VERSION → $1"
fi


bumpversion --allow-dirty --current-version $CURRENT_VERSION $1 setup.py

rm -rf ./dist/*

python setup.py sdist
python setup.py bdist_wheel

if [ $TEST = 1 ]; then
    twine upload --repository testpypi dist/*
else
    echo "Uploading to pypi"
    twine upload -u $PIP_USERNAME -p $PIP_PASSWORD dist/*
fi

VERSION="$(python setup.py --version)"
echo "==================================================================="
echo "Bumped $CURRENT_VERSION → $VERSION ($1 release)"
echo "Uploaded to pypi, check https://pypi.org/project/skale.py/$VERSION/"

#git commit -am "New package version built and published"
