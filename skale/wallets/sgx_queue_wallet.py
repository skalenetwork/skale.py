import enum
import json
import time

from redis import Redis
from skale.wallets.sgx_wallet import SgxWallet
from skale.transactions.exceptions import (
    TransactionError, TransactionFailedError, TransactionNotFoundError)


class SgxQueueWalletError(Exception):
    pass


class QueueTxNotSentError(SgxQueueWalletError, TransactionError):
    pass


class QueueTxNotFoundError(SgxQueueWalletError, TransactionNotFoundError):
    pass


class QueueTxFailedError(SgxQueueWalletError, TransactionFailedError):
    pass


class QueueResponseNotReceivedError(SgxQueueWalletError, TransactionError):
    pass


class QueueInvalidMessageFormatError(SgxQueueWalletError, TransactionError):
    pass


OK_STATUS = 'ok'


class SgxQueueWallet(SgxWallet):
    POST_CHANNEL_TEMPLATE = 'tx.post.{}'
    RECEIPT_CHANNEL_TEMPLATE = 'tx.receipt.{}'
    TIMEOUT = 60 * 30  # 30 minutes

    class ErrorType(enum.Enum):
        NOT_SENT = 'not-sent'
        NOT_FOUND = 'not-found'
        TX_FAILED = 'tx-failed'

    def __init__(self, *args, channel, redis_uri=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.channel = channel
        redis_uri = redis_uri or 'redis://localhost:6379'
        self.redis = Redis.from_url(url=redis_uri, db=0)

    @property
    def post_channel(self) -> str:
        return SgxQueueWallet.POST_CHANNEL_TEMPLATE.format(self.channel)

    @property
    def receipt_channel(self) -> str:
        return SgxQueueWallet.RECEIPT_CHANNEL_TEMPLATE.format(self.channel)

    def compose_tx_message(self, tx: dict) -> dict:
        return {
            'channel': self.channel,
            'tx': tx
        }

    @classmethod
    def parse_message(cls, message: dict) -> tuple:
        msg_data = json.loads(message['data'].decode('utf-8'))
        return msg_data['status'], msg_data['payload']

    def raise_from_error_payload(self, error_payload: dict):
        plain_error_type = error_payload['type']
        error_type = SgxQueueWallet.ErrorType(error_payload['type'])
        msg = error_payload['msg']
        if error_type == SgxQueueWallet.ErrorType.NOT_SENT:
            raise QueueTxNotSentError(f'Channel: {self.channel}, msg: {msg}')
        elif error_type == SgxQueueWallet.ErrorType.NOT_FOUND:
            tx_hash = error_payload['tx_hash']
            raise QueueTxNotFoundError(
                f'Channel: {self.channel}, tx_hash: {tx_hash}, msg: {msg}')
        elif error_type == SgxQueueWallet.ErrorType.TX_FAILED:
            tx_hash = error_payload['tx_hash']
            receipt = error_payload['receipt']
            raise QueueTxFailedError(
                f'Channel: {self.channel}, tx_hash: {tx_hash}, '
                f'receipt: {receipt}')
        else:
            raise QueueInvalidMessageFormatError(
                f'Unsopported errror type: {plain_error_type}'
            )

    @classmethod
    def wait_for_result(cls, sub) -> dict:
        finished = False
        status, payload = None, None
        start_ts = time.time()
        while not finished and time.time() - start_ts < SgxQueueWallet.TIMEOUT:
            msg = sub.get_message()
            if msg['type'] == 'message':
                status, payload = cls.parse_message(msg)
                finished = True
        return finished, status, payload

    def wait_for_receipt(self, tx_dict: dict, *args, **kwargs) -> dict:
        sub = self.redis.pubsub()
        sub.subscribe(self.receipt_channel)
        message = self.compose_tx_message(tx_dict)
        self.redis.publish(self.post_channel, message)

        finished, status, payload = self.wait_for_result(sub)
        if not finished:
            raise QueueResponseNotReceivedError(
                f'Channel: {self.channel}'
            )
        if status == OK_STATUS:
            return payload['tx_hash'], payload['receipt']
        else:
            self.raise_from_error_payload(payload)

    def sign_and_send(self, tx_dict: dict):
        raise NotImplementedError(
            'This method is not supported in SgxQueueWallet')
