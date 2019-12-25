#!/usr/bin/env bash

set -e

: "${ETH_PRIVATE_KEY?Need to set ETH_PRIVATE_KEY}"
: "${USERNAME?Need to set USERNAME}"
: "${PASSWORD?Need to set PASSWORD}"
: "${MANAGER_BRANCH?Need to set MANAGER_BRANCH}"

docker run -d -p 8545:8545 --name ganache trufflesuite/ganache-cli:latest  \
    --account="${ETH_PRIVATE_KEY},100000000000000000000000000" -l 80000000

echo "$PASSWORD" | docker login --username $USERNAME --password-stdin

export DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

docker run -ti \
    -v $DIR/contracts_data:/usr/src/manager/data \
    --network host
    skalelabshub/skale-manager:$MANAGER_BRANCH-latest \
    npx truffle migrate --network test

cp $DIR/contracts_data/test.json $DIR/../test_abi.json
