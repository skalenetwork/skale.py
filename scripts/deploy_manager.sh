#!/usr/bin/env bash

set -e

: "${USERNAME?Need to set USERNAME}"
: "${PASSWORD?Need to set PASSWORD}"

echo "$PASSWORD" | docker login --username $USERNAME --password-stdin

: "${MANAGER_BRANCH?Need to set MANAGER_BRANCH}"
: "${ETH_PRIVATE_KEY?Need to set ETH_PRIVATE_KEY}"
: "${ENDPOINT_HTTP?Need to set ENDPOINT_HTTP}"

export DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

docker run -ti -e PRIVATE_KEY=$ETH_PRIVATE_KEY -e ENDPOINT=$ENDPOINT_HTTP \
    -v $DIR/contracts_data:/usr/src/manager/data \
    skalelabshub/skale-manager:$MANAGER_BRANCH-latest \
    npx truffle migrate --network unique

cp $DIR/contracts_data/unique.json $DIR/../test_abi.json
