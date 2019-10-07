#!/usr/bin/env bash
VERSION=$(python setup.py --version)
USAGE_MSG='Usage: BRANCH=[BRANCH] calculate_version.sh'

if [ -z "$BRANCH" ]
then
    (>&2 echo 'You should provide branch')
    echo $USAGE_MSG
    exit 1
fi


if [ -z $VERSION ]; then
      echo "The base version is not set."
      exit 1
fi


if [[ $BRANCH == 'master' ]]; then
    echo $VERSION
    exit 1
elif [[ $BRANCH == 'develop' ]]; then
    POSTFIX="dev"
elif [[ $BRANCH == 'beta' ]]; then
    POSTFIX="dev"
elif [[ $BRANCH == 'feature/SKALE-1574-automatic-builds' ]]; then
    POSTFIX="a"
else
    echo "Branch is not valid, couldn't calculate version"
    exit 1
fi

git fetch --tags > /dev/null

for (( NUMBER=0; ; NUMBER++ ))
do
    FULL_VERSION="$VERSION$POSTFIX$NUMBER"
    if ! [ $(git tag -l | grep $FULL_VERSION) ]; then
        echo "$FULL_VERSION" | tr / -
        break
    fi
done