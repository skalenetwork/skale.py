import pytest
import mock
from web3 import Web3

from skale.transactions.result import (DryRunFailedError,
                                       InsufficientBalanceError,
                                       TransactionFailedError)
from skale import Skale
from skale.transactions.tools import run_tx_with_retry
from skale.utils.account_tools import generate_account, send_ether
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3
from tests.constants import ENDPOINT, TEST_ABI_FILEPATH, TEST_GAS_LIMIT

ETH_IN_WEI = 10 ** 18


def generate_new_skale():
    web3 = init_web3(ENDPOINT)
    account = generate_account(web3)
    wallet = Web3Wallet(account['private_key'], web3)
    return Skale(ENDPOINT, TEST_ABI_FILEPATH, wallet)


def test_run_tx_with_retry(skale):
    account = generate_account(skale.web3)
    address_to = account['address']
    address_from = Web3.toChecksumAddress(skale.wallet.address)
    address_to = Web3.toChecksumAddress(address_to)
    balance_from_before = skale.token.get_balance(address_from)
    balance_to_before = skale.token.get_balance(address_to)

    token_amount = 10 * ETH_IN_WEI
    tx_res = run_tx_with_retry(
        skale.token.transfer, account['address'], token_amount, wait_for=True,
        max_retries=5
    )
    tx_res.raise_for_status()

    balance_from_after = skale.token.get_balance(address_from)
    assert balance_from_after == balance_from_before - token_amount
    balance_to_after = skale.token.get_balance(address_to)
    assert balance_to_after == balance_to_before + token_amount


def test_run_tx_with_retry_dry_run_failed(skale):
    dry_run_call_mock = mock.Mock(return_value={'status': 0,
                                                'error': 'Dry run failed'})
    account = generate_account(skale.web3)
    token_amount = 10 * ETH_IN_WEI
    retries_number = 5
    with mock.patch('skale.contracts.base_contract.make_dry_run_call',
                    dry_run_call_mock):

        tx_res = run_tx_with_retry(
            skale.token.transfer, account['address'], token_amount,
            wait_for=True, raise_for_status=False,
            max_retries=retries_number
        )
        with pytest.raises(DryRunFailedError):
            tx_res.raise_for_status()

    assert dry_run_call_mock.call_count == retries_number


def test_run_tx_with_retry_tx_failed(patched_wallet_failed_tx_skale):
    skale = patched_wallet_failed_tx_skale
    account = generate_account(skale.web3)
    eth_amount = 5
    # Sending ether to perform transaction
    send_ether(skale.web3, skale.wallet, account['address'], eth_amount)

    token_amount = 10 * ETH_IN_WEI
    retries_number = 5
    tx_res = run_tx_with_retry(
        skale.token.transfer,
        account['address'], token_amount, wait_for=True,
        raise_for_status=False,
        max_retries=retries_number,
    )
    with pytest.raises(TransactionFailedError):
        tx_res.raise_for_status()
    assert skale.wallet.wait_for_receipt.call_count == retries_number


def test_run_tx_with_retry_insufficient_balance(patched_wallet_failed_tx_skale):
    skale = patched_wallet_failed_tx_skale
    wait_for_receipt_by_blocks_mock = mock.Mock()

    sender_skale = generate_new_skale()
    token_amount = 10 * ETH_IN_WEI
    huge_gas_limit = TEST_GAS_LIMIT * 1000000000
    retries_number = 5
    with pytest.raises(InsufficientBalanceError):
        tx_res = run_tx_with_retry(
            sender_skale.token.transfer,
            skale.wallet.address, token_amount, wait_for=True,
            gas_limit=huge_gas_limit,
            skip_dry_run=True,
            raise_for_status=False,
            max_retries=retries_number,
        )
        assert tx_res.tx_hash is None
        assert tx_res.receipt is None
    skale.wallet.wait_for_receipt.asssert_not_called()
    wait_for_receipt_by_blocks_mock.assert_not_called()
