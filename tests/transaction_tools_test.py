from unittest import mock

import pytest
from web3 import Web3

from skale import SkaleManager
from skale.transactions.exceptions import DryRunFailedError, TransactionFailedError
from skale.transactions.tools import (
    TxCallResult,
    TxStatus,
    estimate_gas,
    get_block_gas_limit,
    run_tx_with_retry,
)
from skale.utils.account_tools import generate_account
from skale.utils.helper import get_skale_manager_address
from skale.utils.web3_utils import init_web3
from skale.wallets import Web3Wallet
from skale.wallets.web3_wallet import generate_wallet
from tests.constants import (
    D_VALIDATOR_DESC,
    D_VALIDATOR_FEE,
    D_VALIDATOR_MIN_DEL,
    D_VALIDATOR_NAME,
    ENDPOINT,
    TEST_ABI_FILEPATH,
)

ETH_IN_WEI = 10**18
RETRIES_NUMBER = 2


def generate_new_skale():
    web3 = init_web3(ENDPOINT)
    account = generate_account(web3)
    wallet = Web3Wallet(account['private_key'], web3)
    wallet.wait = mock.Mock()
    return SkaleManager(ENDPOINT, get_skale_manager_address(TEST_ABI_FILEPATH), wallet)


def test_run_tx_with_retry(skale):
    account = generate_account(skale.web3)
    address_to = account['address']
    address_from = Web3.to_checksum_address(skale.wallet.address)
    address_to = Web3.to_checksum_address(address_to)
    balance_from_before = skale.token.get_balance(address_from)
    balance_to_before = skale.token.get_balance(address_to)

    token_amount = 10 * ETH_IN_WEI
    tx_res = run_tx_with_retry(
        skale.token.transfer, account['address'], token_amount, wait_for=True, max_retries=5
    )
    tx_res.raise_for_status()

    balance_from_after = skale.token.get_balance(address_from)
    assert balance_from_after == balance_from_before - token_amount
    balance_to_after = skale.token.get_balance(address_to)
    assert balance_to_after == balance_to_before + token_amount


def test_run_tx_with_retry_dry_run_failed(skale):
    dry_run_call_mock = mock.Mock(
        return_value=TxCallResult(
            status=TxStatus.FAILED, error='revert', message='Dry run test failure', data={}
        )
    )
    account = generate_account(skale.web3)
    token_amount = 10 * ETH_IN_WEI
    with mock.patch('skale.contracts.base_contract.make_dry_run_call', dry_run_call_mock):
        tx_res = run_tx_with_retry(
            skale.token.transfer,
            account['address'],
            token_amount,
            wait_for=True,
            raise_for_status=False,
            max_retries=RETRIES_NUMBER,
        )
        with pytest.raises(DryRunFailedError):
            tx_res.raise_for_status()

    assert dry_run_call_mock.call_count == RETRIES_NUMBER


def test_run_tx_with_retry_tx_failed(failed_skale):
    skale = failed_skale
    account = generate_account(skale.web3)
    token_amount = 10 * ETH_IN_WEI
    tx_res = run_tx_with_retry(
        skale.token.transfer,
        account['address'],
        token_amount,
        wait_for=True,
        raise_for_status=False,
        max_retries=RETRIES_NUMBER,
    )
    with pytest.raises(TransactionFailedError):
        tx_res.raise_for_status()

    assert skale.wallet.sign_and_send.call_count == RETRIES_NUMBER
    assert skale.wallet.wait.call_count == RETRIES_NUMBER


def test_run_tx_with_retry_insufficient_balance(skale):
    sender_skale = generate_new_skale()
    token_amount = 10 * ETH_IN_WEI
    tx_res = run_tx_with_retry(
        sender_skale.token.transfer,
        skale.wallet.address,
        token_amount,
        raise_for_status=False,
        max_retries=RETRIES_NUMBER,
    )

    assert tx_res.attempts == RETRIES_NUMBER


def test_estimate_gas(skale):
    main_wallet = skale.wallet
    skale.wallet = generate_wallet(skale.web3)

    method = skale.validator_service.contract.functions.registerValidator(
        D_VALIDATOR_NAME, D_VALIDATOR_DESC, D_VALIDATOR_FEE, D_VALIDATOR_MIN_DEL
    )
    opts = {'from': skale.wallet.address, 'value': 0}

    block_gas_limit = get_block_gas_limit(skale.web3)
    estimated_gas = estimate_gas(skale.web3, method, opts)

    assert isinstance(estimated_gas, int)
    assert estimated_gas != block_gas_limit

    with mock.patch.object(method, 'estimate_gas', return_value=10000000000):
        estimated_gas = estimate_gas(skale.web3, method, opts)

    assert estimated_gas == block_gas_limit
    skale.wallet = main_wallet


@pytest.mark.skip(reason='This test is not working on the CI')
def test_tx_fee_options(skale):
    account = generate_account(skale.web3)
    address_to = account['address']
    address_from = Web3.to_checksum_address(skale.wallet.address)
    address_to = Web3.to_checksum_address(address_to)
    balance_from_before = skale.token.get_balance(address_from)
    balance_to_before = skale.token.get_balance(address_to)
    token_amount = 10 * ETH_IN_WEI

    max_fee = 10**9
    max_priority_fee = 10**9
    res = skale.token.transfer(
        account['address'],
        token_amount,
        max_fee_per_gas=max_fee,
        max_priority_fee_per_gas=max_priority_fee,
    )
    r = res.receipt
    assert r['effectiveGasPrice'] == max_fee

    balance_from_after = skale.token.get_balance(address_from)
    assert balance_from_after == balance_from_before - token_amount
    balance_to_after = skale.token.get_balance(address_to)
    assert balance_to_after == balance_to_before + token_amount

    skale.token.transfer(
        account['address'],
        token_amount,
        max_fee_per_gas=max_fee,
        max_priority_fee_per_gas=int(max_fee / 2),
    )
