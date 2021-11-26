#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2021-Present SKALE Labs
#
#   SKALE.py is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   SKALE.py is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with SKALE.py.  If not, see <https://www.gnu.org/licenses/>.

import os
import json

from skale.utils.web3_utils import (
    wait_for_receipt_by_blocks
)
from skale.transactions.tools import sign_and_send

# Usage note: to change this contract update the code, compile it and put the new bytecode and
# new ABI below

SAMPLE_CONTRACT = """
pragma solidity ^0.8.0;

contract FakeMultiSigWallet {

    receive() external payable {

    }

    function retrieve() external {
        payable(msg.sender).transfer(address(this).balance);
    }

    constructor() {

    }
}
"""

SAMPLE_CONTRACT_BYTECODE = '608060405234801561001057600080fd5b5060bc8061001f6000396000f3fe608060405260043610601f5760003560e01c80632e64cec114602a576025565b36602557005b600080fd5b348015603557600080fd5b50603c603e565b005b3373ffffffffffffffffffffffffffffffffffffffff166108fc479081150290604051600060405180830381858888f193505050501580156083573d6000803e3d6000fd5b5056fea26469706673582212205da5b248ec5ba69f49e730c2861325b8ad733be642688b5377ec25fc6da7e4fc64736f6c63430008070033'  # noqa

SAMPLE_CONTRACT_ABI = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [],
        "name": "retrieve",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "stateMutability": "payable",
        "type": "receive"
    }
]

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
SAMPLE_CONTRACT_DATA_PATH = os.path.join(DIR_PATH, os.pardir, os.pardir, os.pardir, 'tests',
                                         'sample_contract.json')


def deploy_sample_payable_contract(web3, wallet):
    print('Going to deploy simple payable contract')
    SampleContract = web3.eth.contract(abi=SAMPLE_CONTRACT_ABI, bytecode=SAMPLE_CONTRACT_BYTECODE)
    constructor = SampleContract.constructor()
    tx_hash = sign_and_send(web3, constructor, 100000, wallet)
    receipt = wait_for_receipt_by_blocks(web3, tx_hash)
    print(f'Sample contract successfully deployed: {receipt.contractAddress}')
    content = {
        'address': receipt.contractAddress,
        'abi': SAMPLE_CONTRACT_ABI
    }
    with open(SAMPLE_CONTRACT_DATA_PATH, 'w') as outfile:
        json.dump(content, outfile, indent=4)
    print(f'Sample contract data successfully saved to {SAMPLE_CONTRACT_DATA_PATH}')
