#!/usr/bin/env bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_DIR=$(dirname $DIR)
export ENDPOINT=${ENDPOINT:-http://localhost:8545}
export ENV=test

PYTHONPATH="$PROJECT_DIR/" python "$PROJECT_DIR/tests/allocator/provision_contracts.py"
py.test --cov=$PROJECT_DIR/ $PROJECT_DIR/tests/allocator $@
