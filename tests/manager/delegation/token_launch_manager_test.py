import random
import pytest

from skale.wallets.web3_wallet import generate_wallet
from skale.utils.account_tools import send_ether
from skale.utils.contracts_provision.allocator import transfer_tokens_to_token_launch_manager
from skale.transactions.result import RevertError


N_OF_TOKEN_LAUNCH_WALLETS = 3
MAX_AMOUNT = 100


def generate_and_fund_wallet(skale):
    wallet = generate_wallet(skale.web3)
    send_ether(skale.web3, skale.wallet, wallet.address, 0.1)
    return wallet


def prepare_data(wallets):
    addresses = []
    values = []
    for wallet in wallets:
        addresses.append(wallet.address)
        values.append(random.randint(1, MAX_AMOUNT))
    return addresses, values


def test_approve_transfers(skale):
    transfer_tokens_to_token_launch_manager(skale)
    wallets = [generate_and_fund_wallet(skale) for _ in range(N_OF_TOKEN_LAUNCH_WALLETS)]
    addresses, values = prepare_data(wallets)
    skale.token_launch_manager.approve_batch_of_transfers(addresses, values)

    main_wallet = skale.wallet
    skale.wallet = wallets[0]
    with pytest.raises(RevertError):
        skale.token_launch_manager.retrieve()

    for (i, wallet) in enumerate(wallets):
        value = skale.token_launch_manager.approved(wallet.address)
        assert value == values[i]

    skale.wallet = main_wallet
    skale.token_launch_manager.complete_token_launch()

    for (i, wallet) in enumerate(wallets):
        skale.wallet = wallet
        skale.token_launch_manager.retrieve()
        assert skale.token.get_balance(wallet.address) == values[i]
