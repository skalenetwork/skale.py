#!/usr/bin/env bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_DIR=$(dirname $DIR)
export ENDPOINT=${ENDPOINT:-http://localhost:8545}
export ENV=test

if [ -f "$PROJECT_DIR/helper-scripts/private_key.txt" ]; then
    export ETH_PRIVATE_KEY=$(cat "$PROJECT_DIR/helper-scripts/private_key.txt")
fi

py.test $PROJECT_DIR/tests/ima  $@
