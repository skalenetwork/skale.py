#!/usr/bin/env bash
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
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


if [[ $BRANCH == 'stable' ]]; then
    echo $VERSION
    exit 0
elif [[ $BRANCH == 'develop' ]]; then
    POSTFIX="dev"
elif [[ $BRANCH == 'beta' ]]; then
    POSTFIX="b"
else
    echo "Branch is not valid, couldn't calculate version"
    exit 1
fi

git fetch --tags > /dev/null

for (( NUMBER=0; ; NUMBER++ ))
do
    FULL_VERSION="$VERSION$POSTFIX$NUMBER"
    if ! [[ $(git tag -l | grep $FULL_VERSION) ]]; then
        echo "$FULL_VERSION" | tr / -
        break
    fi
done
