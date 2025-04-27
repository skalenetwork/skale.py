#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_DIR=$(dirname $DIR)

export ENDPOINT=${ENDPOINT:-http://localhost:8545}
export MIRAGE_CONTRACTS=$(bash $PROJECT_DIR/helper-scripts/helper.sh mirage_address)

echo "Running Mirage tests with contracts at $MIRAGE_CONTRACTS"
pytest $PROJECT_DIR/tests/mirage