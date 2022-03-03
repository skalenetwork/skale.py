#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_DIR=$(dirname $DIR)
export ENDPOINT=${ENDPOINT:-http://localhost:8545}
export ENV=test


# python $PROJECT_DIR/tests/prepare_data.py
py.test --cov=$PROJECT_DIR/ $PROJECT_DIR/tests/manager/manager_test.py --ignore $PROJECT_DIR/tests/allocator $@
