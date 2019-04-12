#!/usr/bin/env bash

set -e
set -x

PROJECT_DIR=$(pwd)
PARDIR=$(dirname $PROJECT_DIR)
SKALE_PY_DIR=$PARDIR/skale-py
SKALE_MANAGER_DIR=$PARDIR/skale_blockchain_tools # or skale-manager

export NETWORK="test"
cd $SKALE_MANAGER_DIR
ETH_PRIVATE_KEY=$TEST_ETH_PRIVATE_KEY bash scripts/build.sh

cp $SKALE_MANAGER_DIR/data/$NETWORK.json $SKALE_PY_DIR/skale/envs/$NETWORK.json

python $SKALE_PY_DIR/tests/prepare_data.py

cd $SKALE_PY_DIR
py.test tests/