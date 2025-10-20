"""SKALE test constants"""

import os
from decimal import Decimal

from eth_typing import HexStr

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

DEFAULT_NODE_INDEX = 1
DEFAULT_NODE_NAME = 'test_node'
SECOND_NODE_NAME = 'test_node_2'
DEFAULT_NODE_HASH = '23bdf46c41fa300e431425baff124dc31625b34ec09b829f61aa16ab0102ca8d'
DEFAULT_NODE_PORT = 3000

TEST_CONTRACT_NAME = 'Nodes'
TEST_CONTRACT_NAME_HASH = '51468465ffcfb67cf19598bf6dc259b983b35a0ddf02294ef9b1ce0087c47953'

TOKEN_TRANSFER_VALUE = 100
ETH_TRANSFER_VALUE = Decimal('0.05')

DEFAULT_SCHAIN_NAME = 'test_schain_1'
DEFAULT_SCHAIN_INDEX = 0
DEFAULT_SCHAIN_ID = '0x91bc792a4aa8d4b3ccc3e6acca186f26196ffa90cc391f17a707b829f9479f57'

LIFETIME_YEARS = 1
LIFETIME_SECONDS = LIFETIME_YEARS * 366 * 86400

EMPTY_SCHAIN_ARR = [
    '',
    '0x0000000000000000000000000000000000000000',
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    '0x0000000000000000000000000000000000000000',
]

MIN_NODES_IN_SCHAIN = 2

N_TEST_WALLETS = 2

ENDPOINT = os.environ['ENDPOINT']

HELPER_SCRIPTS_DIR = os.path.join(DIR_PATH, os.pardir, 'helper-scripts')

TEST_ABI_FILEPATH = os.getenv('TEST_ABI_FILEPATH') or os.path.join(
    HELPER_SCRIPTS_DIR, 'contracts_data', 'manager.json'
)
TEST_ALLOCATOR_ABI_FILEPATH = os.getenv('TEST_ALLOCATOR_ABI_FILEPATH') or os.path.join(
    HELPER_SCRIPTS_DIR, 'allocator_contracts_data', 'allocator.json'
)
IMA_DATA_FILEPATH = os.path.join(DIR_PATH, 'ima_data_sample.json')
ETH_PRIVATE_KEY = HexStr(os.environ['ETH_PRIVATE_KEY'])

FAIR_CONTRACTS = os.getenv('FAIR_CONTRACTS')

# constants contract
NEW_REWARD_PERIOD = 600
NEW_DELTA_PERIOD = 400

# sgx wallet
TEST_SGX_ENDPOINT = 'http://localhost:1026'

# rpc wallet
TEST_URL = 'http://localhost:3030'
TEST_RPC_WALLET_URL = 'http://localhost:3000'
NOT_EXISTING_RPC_WALLET_URL = 'http://abc:9999'
EMPTY_HEX_STR = '0x0'

# validator

D_VALIDATOR_ID = 1
D_VALIDATOR_NAME = 'test'
D_VALIDATOR_DESC = 'test'
D_VALIDATOR_FEE = 10
D_VALIDATOR_MIN_DEL = 1000

D_DELEGATION_ID = 0
D_DELEGATION_AMOUNT = 55000000
D_DELEGATION_PERIOD = 2
D_DELEGATION_INFO = 'test'

NOT_EXISTING_ID = 123123

MONTH_IN_SECONDS = 60 * 60 * 24 * 31

DELEGATION_STRUCT_LEN = 8

TEST_ECDSA_KEY_NAME = 'NEK:36224eb0296c6c28c3c73942cf28b5ba449e4a1e6472d52d459627c4d9479b21'

TEST_GAS_LIMIT = 10000000

SCHAIN_FIELDS = [
    'name',
    'mainnet_owner',
    'index_in_owner_list',
    'part_of_node',
    'lifetime',
    'start_date',
    'start_block',
    'deposit',
    'index',
    'generation',
    'originator',
    'chain_id',
    'options',
]
