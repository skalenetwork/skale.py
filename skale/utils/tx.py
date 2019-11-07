import logging
import os

from skale.utils.web3_utils import get_eth_nonce
from skale.utils.wallets.ledger import hardware_sign_and_send

logger = logging.getLogger(__name__)


def software_sign_and_send(web3, method, gas_amount, wallet):
    eth_nonce = get_eth_nonce(web3, wallet['address'])
    logger.info(f'Method {method}. Transaction nonce: {eth_nonce}')
    txn = method.buildTransaction({
        'gas': gas_amount,
        'nonce': eth_nonce  # + 2
    })
    signed_txn = web3.eth.account.signTransaction(
        txn, private_key=wallet['private_key'])
    tx = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    logger.info(
        f'{method.__class__.__name__} - transaction_hash: {web3.toHex(tx)}'
    )
    return tx


def sign_and_send(web3, method, gas_amount, wallet):
    if os.getenv('WALLET') == 'LEDGER':
        res = hardware_sign_and_send(web3, method, gas_amount, wallet)
    else:
        res = software_sign_and_send(web3, method, gas_amount, wallet)
    return res


def send_eth(web3, account, amount, wallet):
    eth_nonce = get_eth_nonce(web3, wallet['address'])
    logger.info(f'Transaction nonce {eth_nonce}')
    txn = {
        'to': account,
        'from': wallet['address'],
        'value': amount,
        'gasPrice': web3.eth.gasPrice,
        'gas': 22000,
        'nonce': eth_nonce
    }
    signed_txn = web3.eth.account.signTransaction(
        txn, private_key=wallet['private_key'])
    tx = web3.eth.sendRawTransaction(signed_txn.rawTransaction)

    logger.info(
        f'ETH transfer {wallet["address"]} => {account}, {amount} wei, tx: {web3.toHex(tx)}'
    )
    return tx
