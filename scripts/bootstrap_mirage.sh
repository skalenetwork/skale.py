#!/usr/bin/env bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_DIR=$(dirname $DIR)
export ENDPOINT=${ENDPOINT:-http://127.0.0.1:8545}

SM_ABI_FILEPATH=${ABI_FILEPATH:="$PROJECT_DIR/helper-scripts/contracts_data/manager.json"}
export MANAGER_CONTRACTS=$(jq -r '.skale_manager_address' "$SM_ABI_FILEPATH")

echo "Going to bootstrap Mirage with ${ENDPOINT} and ${MANAGER_CONTRACTS}"
python skale/utils/contracts_provision/mirage.py