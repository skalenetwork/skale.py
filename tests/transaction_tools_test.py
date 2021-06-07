import mock
import pytest
from web3 import Web3

from skale.transactions.exceptions import (
    DryRunFailedError,
    TransactionFailedError
)
from skale import Skale
from skale.transactions.tools import (
    run_tx_with_retry, send_eth_with_skale, estimate_gas, get_block_gas_limit
)
from skale.utils.account_tools import (
    generate_account,
    send_ether
)
from skale.utils.web3_utils import init_web3, wait_receipt
from skale.wallets import Web3Wallet
from skale.wallets.web3_wallet import generate_wallet

from tests.constants import ENDPOINT, TEST_ABI_FILEPATH, TEST_GAS_LIMIT
from tests.constants import (
    D_VALIDATOR_NAME, D_VALIDATOR_DESC,
    D_VALIDATOR_FEE, D_VALIDATOR_MIN_DEL,
)

ETH_IN_WEI = 10 ** 18


def generate_new_skale():
    web3 = init_web3(ENDPOINT)
    account = generate_account(web3)
    wallet = Web3Wallet(account['private_key'], web3)
    wallet.sign_and_send = mock.Mock()
    wallet.wait = mock.Mock()
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


def test_run_tx_with_retry_tx_failed(failed_skale):
    skale = failed_skale

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

    assert skale.wallet.sign_and_send.call_count == retries_number
    assert skale.wallet.wait.call_count == retries_number


def test_run_tx_with_retry_insufficient_balance(skale):
    sender_skale = generate_new_skale()
    token_amount = 10 * ETH_IN_WEI
    skale.token.transfer(sender_skale.wallet.address, token_amount + 1,
                         skip_dry_run=True,
                         wait_for=True,
                         gas_limit=TEST_GAS_LIMIT)
    retries_number = 5
    sender_skale.wallet.wait = mock.Mock()
    run_tx_with_retry(
        sender_skale.token.transfer,
        skale.wallet.address, token_amount, wait_for=True,
        raise_for_status=False,
        max_retries=retries_number,
    )

    assert skale.wallet.wait.call_count == retries_number


def test_send_eth_with_skale(skale):
    account = generate_account(skale.web3)
    address_to = account['address']
    address_from = Web3.toChecksumAddress(skale.wallet.address)
    address_to = Web3.toChecksumAddress(address_to)
    balance_from_before = skale.web3.eth.getBalance(address_from)
    balance_to_before = skale.web3.eth.getBalance(address_to)
    nonce = skale.web3.eth.getTransactionCount(skale.wallet.address)

    token_amount = 10 * ETH_IN_WEI
    send_eth_with_skale(skale, address_to, token_amount, nonce=nonce)

    fee_value = 10000
    balance_from_after = skale.web3.eth.getBalance(address_from)
    assert balance_from_after - balance_from_before + token_amount < fee_value
    balance_to_after = skale.web3.eth.getBalance(address_to)
    assert balance_to_after == balance_to_before + token_amount


def test_send_eth_with_skale_without_wait_for_false(skale):
    account = generate_account(skale.web3)
    address_to = account['address']
    address_from = Web3.toChecksumAddress(skale.wallet.address)
    address_to = Web3.toChecksumAddress(address_to)
    balance_from_before = skale.web3.eth.getBalance(address_from)
    balance_to_before = skale.web3.eth.getBalance(address_to)

    token_amount = 10 * ETH_IN_WEI
    tx_hash = send_eth_with_skale(skale, address_to,
                                  token_amount, wait_for=False)
    receipt = wait_receipt(skale.web3, tx_hash)
    assert receipt['status'] == 1

    fee_value = 10000
    balance_from_after = skale.web3.eth.getBalance(address_from)
    assert balance_from_after - balance_from_before + token_amount < fee_value
    balance_to_after = skale.web3.eth.getBalance(address_to)
    assert balance_to_after == balance_to_before + token_amount


def test_estimate_gas(skale):
    main_wallet = skale.wallet
    skale.wallet = generate_wallet(skale.web3)

    method = skale.validator_service.contract.functions.registerValidator(
        D_VALIDATOR_NAME,
        D_VALIDATOR_DESC,
        D_VALIDATOR_FEE,
        D_VALIDATOR_MIN_DEL
    )
    opts = {
        'from': skale.wallet.address,
        'value': 0
    }

    block_gas_limit = get_block_gas_limit(skale.web3)
    estimated_gas = estimate_gas(skale.web3, method, opts)

    assert isinstance(estimated_gas, int)
    assert estimated_gas != block_gas_limit

    with mock.patch.object(method, 'estimateGas', return_value=10000000000):
        estimated_gas = estimate_gas(skale.web3, method, opts)

    assert estimated_gas == block_gas_limit
    skale.wallet = main_wallet
