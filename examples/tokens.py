import click
import skale.utils.helper as Helper

from web3 import Web3
from skale import Skale
from skale.utils.account_tools import init_wallet
from skale.utils.hw import hw_transaction
from examples.helper import ENDPOINT, ABI_FILEPATH

Helper.init_default_logger()


@click.group()
@click.option('--endpoint', default=ENDPOINT, help='skale manager endpoint')
@click.option('--abi-filepath', default=ABI_FILEPATH, help='abi file')
@click.pass_context
def main(ctx, endpoint, abi_filepath):
    ctx.ensure_object(dict)
    ctx.obj['skale'] = Skale(endpoint, abi_filepath)


def exec_hw_transaction(skale, wallet):
    hw_transaction(skale, wallet)


def token_transfer(skale, wallet, address_to, tokens_amount):
    from skale.utils.helper import private_key_to_address
    print('NADDRESS {}'.format(private_key_to_address('ACFE994DEE1F8067A02A2DF939B58FFF0FEDB0DA720E5D279CB80EF5637B3530')))
    address_from = Web3.toChecksumAddress('1057dc7277a319927D3eB43e05680B75a00eb5f4')
    address_to = Web3.toChecksumAddress(address_to)
    print(f'ETH BALANCE TO {skale.web3.eth.getBalance(address_to)}')
    balance_from_before = skale.token.get_balance(address_from)
    balance_to_before = skale.token.get_balance(address_to)
    print('BALANCE FROM BEFORE {}'.format(balance_from_before))
    print('BALANCE TO BEFORE {}'.format(balance_to_before))

    res = skale.token.transfer(address_to, tokens_amount, wallet)
    receipt = Helper.await_receipt(skale.web3, res['tx'])

    balance_from_after = skale.token.get_balance(address_from)
    balance_to_after = skale.token.get_balance(address_to)
    print('BALANCE FROM AFTER {}'.format(balance_from_after))
    print('BALANCE TO AFTER {}'.format(balance_to_after))
    print(balance_from_before - balance_from_after)
    print(balance_to_after - balance_to_before)
    return receipt


@main.command()
@click.pass_context
def hw_tx(ctx):
    """ Command for simple hw transaction """
    skale = ctx.obj['skale']
    wallet = init_wallet()
    exec_hw_transaction(skale, wallet)


@main.command()
@click.pass_context
@click.argument('address_to')
@click.argument('tokens_amount', type=int)
def transfer(ctx, address_to, tokens_amount):
    """ Command for transfering tokens to address """
    skale = ctx.obj['skale']
    wallet = init_wallet()
    receipt = token_transfer(skale, wallet, address_to, tokens_amount)
    Helper.check_receipt(receipt)


if __name__ == "__main__":
    main()
