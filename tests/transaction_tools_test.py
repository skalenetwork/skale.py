import pytest
import mock
from web3 import Web3

from skale.dataclasses.tx_res import TransactionFailedError, DryRunFailedError
from skale.transactions.tools import run_tx_with_retry
from skale.utils.account_tools import generate_account


ETH_IN_WEI = 10 ** 18


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


def test_run_tx_with_retry_tx_failed(skale):
    post_transaction_mock = mock.Mock(
        return_value='0xsfrfjerpkjorewjgoierjgowrjgoeirgerg')

    wait_for_receipt_by_blocks_mock = mock.Mock(
        return_value={'status': 0}
    )

    account = generate_account(skale.web3)
    token_amount = 10 * ETH_IN_WEI
    retries_number = 5
    with mock.patch('skale.contracts.base_contract.post_transaction',
                    post_transaction_mock):
        with mock.patch(
            'skale.contracts.base_contract.wait_for_receipt_by_blocks',
            wait_for_receipt_by_blocks_mock
        ):
            tx_res = run_tx_with_retry(
                skale.token.transfer,
                account['address'], token_amount, wait_for=True,
                raise_for_status=False,
                max_retries=retries_number,
            )
            with pytest.raises(TransactionFailedError):
                tx_res.raise_for_status()

            assert post_transaction_mock.call_count == retries_number
            assert wait_for_receipt_by_blocks_mock.call_count == retries_number
