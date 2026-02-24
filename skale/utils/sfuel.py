#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2026-Present SKALE Labs
#
#   SKALE.py is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   SKALE.py is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with SKALE.py.  If not, see <https://www.gnu.org/licenses/>.

import secrets
from dataclasses import dataclass
from time import perf_counter

from eth_account import Account
from hexbytes import HexBytes
from web3 import HTTPProvider, Web3

MAX_NUMBER = (1 << 256) - 1
DEFAULT_DIFFICULTY = 1
DEFAULT_TARGET_GAS = 1_000_000
DEFAULT_MINE_TIMEOUT_SECONDS = 60
DEFAULT_RECEIPT_TIMEOUT_SECONDS = 240

FAUCET_BY_CHAIN_ID: dict[int, tuple[str, str]] = {
    1_444_673_419: ('0x366727B410fE55774C8b0B5b5A6E2d74199a088A', '0x0c11dedd'),
}


@dataclass(frozen=True)
class MiningResult:
    success: bool
    tx_hash: HexBytes | None = None
    receipt_status: int | None = None
    gas_price: int | None = None
    iterations: int | None = None
    elapsed_ms: float | None = None
    start_balance: int | None = None
    end_balance: int | None = None
    balance_delta: int | None = None
    message: str | None = None


def _get_web3(endpoint_or_provider: str | Web3) -> Web3:
    if isinstance(endpoint_or_provider, Web3):
        return endpoint_or_provider
    return Web3(HTTPProvider(endpoint_or_provider, request_kwargs={'timeout': 30}))


def _mine_gas_price(
    nonce: int,
    gas_amount: int,
    from_address: str,
    difficulty: int = DEFAULT_DIFFICULTY,
    timeout_seconds: int = DEFAULT_MINE_TIMEOUT_SECONDS,
) -> tuple[int, int, float]:
    if difficulty < 1:
        raise ValueError('difficulty must be >= 1')

    nonce_hash = int.from_bytes(
        Web3.keccak(nonce.to_bytes(32, byteorder='big', signed=False)),
        byteorder='big',
        signed=False,
    )
    address_hash = int.from_bytes(
        Web3.keccak(hexstr=Web3.to_checksum_address(from_address)),
        byteorder='big',
        signed=False,
    )
    seed = nonce_hash ^ address_hash
    div_constant = MAX_NUMBER // difficulty

    start = perf_counter()
    iterations = 0

    while True:
        candidate = secrets.token_bytes(32)
        candidate_hash = int.from_bytes(Web3.keccak(candidate), byteorder='big', signed=False)
        result_hash = seed ^ candidate_hash
        if result_hash != 0 and div_constant // result_hash >= gas_amount:
            elapsed_ms = (perf_counter() - start) * 1_000.0
            gas_price = int.from_bytes(candidate, byteorder='big', signed=False)
            return gas_price, iterations + 1, elapsed_ms
        iterations += 1
        if timeout_seconds > 0 and (perf_counter() - start) >= timeout_seconds:
            raise TimeoutError(f'PoW mining exceeded timeout ({timeout_seconds}s).')


def mine_sfuel(
    endpoint_or_provider: str | Web3,
    beneficiary_address: str,
    faucet_address: str | None = None,
    faucet_func: str | None = None,
) -> MiningResult:
    web3 = _get_web3(endpoint_or_provider)
    if not web3.is_connected():
        raise ConnectionError('Unable to connect to provider.')

    chain_id = int(web3.eth.chain_id)

    if faucet_address and faucet_func:
        function_selector = faucet_func
    else:
        faucet = FAUCET_BY_CHAIN_ID.get(chain_id)
        if faucet is None:
            return MiningResult(
                success=False,
                message=f'Unsupported chain id for sFUEL faucet: {chain_id}',
            )
        faucet_address, function_selector = faucet

    if len(function_selector) != 10 or not function_selector.startswith('0x'):
        return MiningResult(success=False, message='Invalid faucet function selector.')

    faucet_checksum = web3.to_checksum_address(faucet_address)
    if len(web3.eth.get_code(faucet_checksum)) == 0:
        return MiningResult(
            success=False,
            message=f'Configured faucet has no contract code: {faucet_checksum}',
        )

    beneficiary_checksum = web3.to_checksum_address(beneficiary_address)
    start_balance = int(web3.eth.get_balance(beneficiary_checksum))

    ephemeral = Account.create()
    nonce = int(web3.eth.get_transaction_count(ephemeral.address))
    gas_price, iterations, elapsed_ms = _mine_gas_price(
        nonce=nonce,
        gas_amount=DEFAULT_TARGET_GAS,
        from_address=ephemeral.address,
    )

    encoded_param = web3.codec.encode(['address'], [beneficiary_checksum]).hex()
    data = function_selector + encoded_param
    tx = {
        'nonce': nonce,
        'to': faucet_checksum,
        'value': 0,
        'gas': DEFAULT_TARGET_GAS,
        'gasPrice': gas_price,
        'chainId': chain_id,
        'data': data,
    }

    signed = web3.eth.account.sign_transaction(tx, private_key=ephemeral.key)
    tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = web3.eth.wait_for_transaction_receipt(
        tx_hash,
        timeout=DEFAULT_RECEIPT_TIMEOUT_SECONDS,
    )

    receipt_status = int(receipt.get('status', 0))
    end_balance = int(web3.eth.get_balance(beneficiary_checksum))
    balance_delta = end_balance - start_balance
    success = receipt_status == 1 and balance_delta > 0

    if success:
        message = 'sFUEL funding completed.'
    elif receipt_status != 1:
        message = f'Funding transaction failed with receipt status {receipt_status}.'
    else:
        message = 'Funding transaction succeeded but beneficiary balance did not increase.'

    return MiningResult(
        success=success,
        tx_hash=tx_hash,
        receipt_status=receipt_status,
        gas_price=gas_price,
        iterations=iterations,
        elapsed_ms=elapsed_ms,
        start_balance=start_balance,
        end_balance=end_balance,
        balance_delta=balance_delta,
        message=message,
    )
