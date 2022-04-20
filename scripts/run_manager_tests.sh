#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_DIR=$(dirname $DIR)
export ENDPOINT=${ENDPOINT:-http://localhost:8545}
export ENV=test


py.test --cov=$PROJECT_DIR/ $PROJECT_DIR/tests/rotation_history/rotation_history_test.py --ignore $PROJECT_DIR/tests/allocator $@
