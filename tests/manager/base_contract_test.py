import importlib
import os

import mock
import pytest
import skale.config as config
from skale.transactions.result import InsufficientBalanceError
from skale.transactions.tools import estimate_gas
from skale.utils.account_tools import generate_account
from skale.utils.web3_utils import wait_for_receipt_by_blocks
from tests.constants import TEST_GAS_LIMIT
from web3 import Web3

ETH_IN_WEI = 10 ** 18
CUSTOM_DEFAULT_GAS_LIMIT = 2 * 10 ** 6
CUSTOM_DEFAULT_GAS_PRICE_WEI = 1500000000


def test_dry_run(skale):
    account = generate_account(skale.web3)
    address_to = account['address']
    address_from = Web3.toChecksumAddress(skale.wallet.address)
    address_to = Web3.toChecksumAddress(address_to)
    balance_from_before = skale.token.get_balance(address_from)
    balance_to_before = skale.token.get_balance(address_to)
    amount = 10 * ETH_IN_WEI
    tx_res = skale.token.transfer(address_to, amount, dry_run_only=True)
    assert isinstance(tx_res.dry_run_result['payload'], int)
    assert tx_res.dry_run_result['status'] == 1
    tx_res.raise_for_status()

    balance_from_after = skale.token.get_balance(address_from)
    assert balance_from_after == balance_from_before
    balance_to_after = skale.token.get_balance(address_to)
    assert balance_to_after == balance_to_before


@pytest.fixture
def disable_dry_run_env():
    os.environ['DISABLE_DRY_RUN'] = 'True'
    os.environ['DEFAULT_GAS_LIMIT'] = str(CUSTOM_DEFAULT_GAS_LIMIT)
    os.environ['DEFAULT_GAS_PRICE_WEI'] = str(CUSTOM_DEFAULT_GAS_PRICE_WEI)
    importlib.reload(config)
    yield
    os.environ.pop('DISABLE_DRY_RUN')
    os.environ.pop('DEFAULT_GAS_LIMIT')
    importlib.reload(config)


def test_disable_dry_run_env(skale, disable_dry_run_env):
    account = generate_account(skale.web3)
    address_to = account['address']
    amount = 10 * ETH_IN_WEI
    with mock.patch(
        'skale.contracts.base_contract.execute_dry_run'
    ) as dry_run_mock:
        with mock.patch(
            'skale.contracts.base_contract.post_transaction'
        ) as post_transaction_mock:
            skale.token.transfer(address_to, amount, wait_for=False)
            dry_run_mock.assert_not_called()
            assert post_transaction_mock.call_args[0][2] == \
                CUSTOM_DEFAULT_GAS_LIMIT
            assert post_transaction_mock.call_args[0][6] == \
                CUSTOM_DEFAULT_GAS_PRICE_WEI


def test_skip_dry_run(skale):
    account = generate_account(skale.web3)
    address_to = account['address']
    address_from = Web3.toChecksumAddress(skale.wallet.address)
    address_to = Web3.toChecksumAddress(address_to)
    balance_from_before = skale.token.get_balance(address_from)
    balance_to_before = skale.token.get_balance(address_to)
    amount = 10 * ETH_IN_WEI

    with mock.patch(
        'skale.contracts.base_contract.config.DEFAULT_GAS_LIMIT', None
    ):
        with pytest.raises(InsufficientBalanceError) as err:
            skale.token.transfer(address_to, amount, skip_dry_run=True)
            assert err == 'Gas limit is empty'

    tx_res = skale.token.transfer(address_to, amount,
                                  skip_dry_run=True, gas_limit=TEST_GAS_LIMIT)
    assert tx_res.tx_hash is not None, tx_res
    assert tx_res.receipt is not None
    assert tx_res.dry_run_result is None
    balance_from_after = skale.token.get_balance(address_from)
    assert balance_from_after == balance_from_before - amount
    balance_to_after = skale.token.get_balance(address_to)
    assert balance_to_after == balance_to_before + amount


def test_wait_for_false(skale):
    ETH_IN_WEI = 10 ** 18
    account = generate_account(skale.web3)
    address_to = account['address']
    address_from = Web3.toChecksumAddress(skale.wallet.address)
    address_to = Web3.toChecksumAddress(address_to)
    balance_from_before = skale.token.get_balance(address_from)
    balance_to_before = skale.token.get_balance(address_to)
    amount = 10 * ETH_IN_WEI

    tx_res = skale.token.transfer(address_to, amount, wait_for=False)
    assert tx_res.tx_hash is not None
    assert tx_res.receipt is None
    assert isinstance(tx_res.dry_run_result['payload'], int)
    assert tx_res.dry_run_result['status'] == 1

    tx_res.receipt = wait_for_receipt_by_blocks(skale.web3, tx_res.tx_hash)
    tx_res.raise_for_status()

    balance_from_after = skale.token.get_balance(address_from)
    assert balance_from_after == balance_from_before - amount
    balance_to_after = skale.token.get_balance(address_to)
    assert balance_to_after == balance_to_before + amount


def test_tx_res_dry_run(skale):
    account = generate_account(skale.web3)
    token_amount = 10
    tx_res = skale.token.transfer(
        account['address'], token_amount, dry_run_only=True)
    assert tx_res.dry_run_result is not None
    assert tx_res.tx_hash is None
    assert tx_res.receipt is None
    tx_res.raise_for_status()


def test_tx_res_wait_for_false(skale):
    account = generate_account(skale.web3)
    token_amount = 10
    tx_res = skale.token.transfer(
        account['address'], token_amount, wait_for=False)
    assert tx_res.tx_hash is not None
    assert tx_res.receipt is None
    tx_res.raise_for_status()

    tx_res.receipt = wait_for_receipt_by_blocks(skale.web3, tx_res.tx_hash)
    tx_res.raise_for_status()


def test_tx_res_wait_for_true(skale):
    account = generate_account(skale.web3)
    token_amount = 10
    tx_res = skale.token.transfer(account['address'], token_amount)
    assert tx_res.tx_hash is not None
    assert tx_res.receipt is not None
    tx_res.raise_for_status()


@mock.patch('skale.contracts.base_contract.account_eth_balance_wei',
            new=mock.Mock(return_value=0))
def test_tx_res_with_insufficient_funds(skale):
    account = generate_account(skale.web3)
    token_amount = 10
    with pytest.raises(InsufficientBalanceError):
        skale.token.transfer(account['address'], token_amount)


def test_confirmation_blocks(skale):
    account = generate_account(skale.web3)
    token_amount = 10
    confirmation_blocks = 0  # todo: enable mining on ganache
    start_block = skale.web3.eth.blockNumber
    skale.token.transfer(account['address'], token_amount, confirmation_blocks=confirmation_blocks)
    assert skale.web3.eth.blockNumber >= start_block + confirmation_blocks


def test_block_limit_estimate_gas(skale):
    account = generate_account(skale.web3)
    token_amount = 10
    max_gas = 200000000
    with mock.patch.object(skale.token.contract.functions.transfer, 'estimateGas',
                           new=mock.Mock(return_value=max_gas)):
        method = skale.token.contract.functions.transfer(account['address'], token_amount)
        res = estimate_gas(skale.web3, method, {'from': skale.wallet.address})
        assert res < max_gas
