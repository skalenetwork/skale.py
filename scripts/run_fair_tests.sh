#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_DIR=$(dirname $DIR)

export ENDPOINT=${ENDPOINT:-http://localhost:8545}
export FAIR_CONTRACTS=$(bash $PROJECT_DIR/helper-scripts/helper.sh fair_address)

echo "Running Fair tests with contracts at $FAIR_CONTRACTS"
uv run pytest $PROJECT_DIR/tests/fair