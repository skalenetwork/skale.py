#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_DIR=$(dirname $DIR)

python $PROJECT_DIR/tests/prepare_data.py
py.test --cov=$PROJECT_DIR/ $PROJECT_DIR/tests/contracts/schains_internal_test.py::test_get_active_schain_ids
