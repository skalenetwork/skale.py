#   -*- coding: utf-8 -*-
#
#   This file is part of SKALE.py
#
#   Copyright (C) 2019-Present SKALE Labs
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

from skale.utils.contracts_provision import (
    D_VALIDATOR_ID, D_VALIDATOR_MIN_DEL, D_DELEGATION_PERIOD, D_DELEGATION_INFO,
    D_VALIDATOR_NAME, D_VALIDATOR_DESC, D_VALIDATOR_FEE, DEFAULT_NODE_NAME, SECOND_NODE_NAME,
    DEFAULT_SCHAIN_NAME, FIRST_DELEGATION_MONTH
)
from skale.utils.contracts_provision.utils import (
    generate_random_node_data, generate_random_schain_data
)


def _skip_evm_time(web3, seconds) -> int:
    """For test purposes only, works only with ganache node"""
    res = web3.provider.make_request("evm_increaseTime", [seconds])
    web3.provider.make_request("evm_mine", [])
    return res['result']


def cleanup_nodes_schains(skale):
    print('Cleanup nodes and schains')
    for schain_id in skale.schains_internal.get_all_schains_ids():
        schain_data = skale.schains.get(schain_id)
        schain_name = schain_data.get('name', None)
        if schain_name is not None:
            skale.manager.delete_schain(schain_name, wait_for=True)
    for node_id in skale.nodes.get_active_node_ids():
        skale.manager.node_exit(node_id, wait_for=True)


def validator_exist(skale):
    return skale.validator_service.number_of_validators() > 0


def setup_validator(skale):
    """Create and activate a validator"""
    if not validator_exist(skale):
        create_validator(skale)
        enable_validator(skale)
    else:
        print('Skipping default validator creation')
    set_test_msr(skale)
    skale.constants_holder.set_first_delegation_month(FIRST_DELEGATION_MONTH)
    delegate_to_validator(skale)
    delegations = skale.delegation_controller.get_all_delegations_by_validator(D_VALIDATOR_ID)
    accept_pending_delegation(skale, delegations[-1]['id'])


def link_address_to_validator(skale):
    print('Linking address to validator')
    signature = skale.validator_service.get_link_node_signature(D_VALIDATOR_ID)
    tx_res = skale.validator_service.link_node_address(
        node_address=skale.wallet.address,
        signature=signature,
        wait_for=True
    )
    tx_res.raise_for_status()


def skip_delegation_delay(skale, delegation_id):
    print(f'Activating delegation with ID {delegation_id}')
    skale.token_state._skip_transition_delay(
        delegation_id,
        wait_for=True
    )


def accept_pending_delegation(skale, delegation_id):
    print(f'Accepting delegation with ID: {delegation_id}')
    skale.delegation_controller.accept_pending_delegation(
        delegation_id=delegation_id,
        wait_for=True
    )


def get_test_delegation_amount(skale):
    msr = skale.constants_holder.msr()
    return msr * 30


def set_test_msr(skale):
    skale.constants_holder._set_msr(
        new_msr=D_VALIDATOR_MIN_DEL,
        wait_for=True
    )


def delegate_to_validator(skale):
    print(f'Delegating tokens to validator ID: {D_VALIDATOR_ID}')
    skale.delegation_controller.delegate(
        validator_id=D_VALIDATOR_ID,
        amount=get_test_delegation_amount(skale),
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        wait_for=True
    )


def enable_validator(skale):
    print(f'Enabling validator ID: {D_VALIDATOR_ID}')
    skale.validator_service._enable_validator(D_VALIDATOR_ID, wait_for=True)


def create_validator(skale):
    print('Creating default validator')
    skale.validator_service.register_validator(
        name=D_VALIDATOR_NAME,
        description=D_VALIDATOR_DESC,
        fee_rate=D_VALIDATOR_FEE,
        min_delegation_amount=D_VALIDATOR_MIN_DEL,
        wait_for=True
    )


def create_nodes(skale):
    # create couple of nodes
    print('Creating two nodes')
    node_names = [DEFAULT_NODE_NAME, SECOND_NODE_NAME]
    for name in node_names:
        ip, public_ip, port, _ = generate_random_node_data()
        skale.manager.create_node(ip, port, name, public_ip, wait_for=True)


def create_schain(skale, schain_name=DEFAULT_SCHAIN_NAME):
    print('Creating schain')
    # create 1 s-chain
    type_of_nodes, lifetime_seconds, _ = generate_random_schain_data()
    price_in_wei = skale.schains.get_schain_price(type_of_nodes,
                                                  lifetime_seconds)

    skale.manager.create_schain(
        lifetime_seconds,
        type_of_nodes,
        price_in_wei,
        schain_name,
        wait_for=True
    )
