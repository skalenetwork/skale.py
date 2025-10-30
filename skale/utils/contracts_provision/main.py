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

from typing import List, Tuple

from eth_typing import ChecksumAddress
from web3 import Web3
from web3.types import RPCEndpoint

from skale import SkaleManager
from skale.dataclasses.schain_options import SchainOptions
from skale.transactions.result import TxRes
from skale.types.node import NodeId, NodeStatus
from skale.types.schain import SchainName
from skale.types.validator import ValidatorId
from skale.utils.contracts_provision import (
    D_DELEGATION_INFO,
    D_DELEGATION_PERIOD,
    D_STAKE_MULTIPLIER,
    D_VALIDATOR_DESC,
    D_VALIDATOR_FEE,
    D_VALIDATOR_ID,
    D_VALIDATOR_MIN_DEL,
    D_VALIDATOR_NAME,
    DEFAULT_DOMAIN_NAME,
    DEFAULT_NODE_NAME,
    DEFAULT_SCHAIN_NAME,
    INITIAL_DELEGATION_PERIOD,
    MONTH_IN_SECONDS,
    SECOND_NODE_NAME,
)
from skale.utils.contracts_provision.utils import (
    generate_random_node_data,
    generate_random_schain_data,
)

DEFAULT_MINING_INTERVAL = 1000
TEST_SRW_FUND_VALUE = 3000000000000000000


def _skip_evm_time(web3: Web3, seconds: int, mine: bool = True) -> int:
    """For test purposes only, works only with hardhat node"""
    res = web3.provider.make_request(RPCEndpoint('evm_increaseTime'), [seconds])
    if mine:
        web3.provider.make_request(RPCEndpoint('evm_mine'), [])
    return int(res['result'])


def set_automining(web3: Web3, value: bool) -> int:
    res = web3.provider.make_request(RPCEndpoint('evm_setAutomine'), [value])
    return int(res['result'])


def set_mining_interval(web3: Web3, ms: int) -> None:
    web3.provider.make_request(RPCEndpoint('evm_setIntervalMining'), [ms])


def set_default_mining_interval(web3: Web3) -> None:
    set_mining_interval(web3, DEFAULT_MINING_INTERVAL)


def add_test_permissions(skale: SkaleManager) -> None:
    add_all_permissions(skale, skale.wallet.address)


def add_all_permissions(skale: SkaleManager, address: ChecksumAddress) -> None:
    default_admin_role = skale.manager.default_admin_role()
    if not skale.manager.has_role(default_admin_role, address):
        skale.manager.grant_role(default_admin_role, address)

    schain_creator_role = skale.schains.schain_creator_role()
    if not skale.schains.has_role(schain_creator_role, address):
        skale.schains.grant_role(schain_creator_role, address)

    schain_removal_role = skale.manager.schain_removal_role()
    if not skale.manager.has_role(schain_removal_role, address):
        skale.manager.grant_role(schain_removal_role, address)

    bounty_reduction_manager_role = skale.bounty_v2.bounty_reduction_manager_role()
    if not skale.bounty_v2.has_role(bounty_reduction_manager_role, address):
        skale.bounty_v2.grant_role(bounty_reduction_manager_role, address)

    locker_manager_role = skale.token_state.locker_manager_role()
    if not skale.token_state.has_role(locker_manager_role, address):
        skale.token_state.grant_role(locker_manager_role, address)

    schain_type_manager_role = skale.schains_internal.schain_type_manager_role()
    if not skale.schains_internal.has_role(schain_type_manager_role, address):
        skale.schains_internal.grant_role(schain_type_manager_role, address)

    validator_manager_role = skale.validator_service.validator_manager_role()
    if not skale.validator_service.has_role(validator_manager_role, address):
        skale.validator_service.grant_role(validator_manager_role, address)

    node_manager_role = skale.nodes.node_manager_role()
    if not skale.nodes.has_role(node_manager_role, address):
        skale.nodes.grant_role(node_manager_role, address)

    compliance_role = skale.nodes.compliance_role()
    if not skale.nodes.has_role(compliance_role, address):
        skale.nodes.grant_role(compliance_role, address)

    constants_holder_role = skale.constants_holder.constants_holder_role()
    if not skale.constants_holder.has_role(constants_holder_role, address):
        skale.constants_holder.grant_role(constants_holder_role, address)

    debugger_role = skale.node_rotation.debugger_role()
    if not skale.node_rotation.has_role(debugger_role, address):
        skale.node_rotation.grant_role(debugger_role, address)

    debugger_schains_role = skale.schains_internal.debugger_role()
    if not skale.schains_internal.has_role(debugger_schains_role, address):
        skale.schains_internal.grant_role(debugger_schains_role, address)

    generation_manager_role = skale.schains_internal.generation_manager_role()
    if not skale.schains_internal.has_role(generation_manager_role, address):
        skale.schains_internal.grant_role(generation_manager_role, address)

    forgiver_role = skale.punisher.forgiver_role()
    if not skale.punisher.has_role(forgiver_role, address):
        skale.punisher.grant_role(forgiver_role, address)

    delegation_period_setter_role = skale.delegation_period_manager.delegation_period_setter_role()
    if not skale.delegation_period_manager.has_role(delegation_period_setter_role, address):
        skale.delegation_period_manager.grant_role(delegation_period_setter_role, address)

    penalty_setter_role = skale.slashing_table.penalty_setter_role()
    if not skale.slashing_table.has_role(penalty_setter_role, address):
        skale.slashing_table.grant_role(penalty_setter_role, address)


def add_test2_schain_type(skale: SkaleManager) -> TxRes:
    part_of_node = 1
    number_of_nodes = 2
    return skale.schains_internal.add_schain_type(part_of_node, number_of_nodes)


def add_test4_schain_type(skale: SkaleManager) -> TxRes:
    part_of_node = 1
    number_of_nodes = 4
    return skale.schains_internal.add_schain_type(part_of_node, number_of_nodes)


def cleanup_nodes(skale: SkaleManager, ids: list[NodeId] | None = None) -> None:
    active_ids = filter(
        lambda i: skale.nodes.get_node_status(i) == NodeStatus.ACTIVE,
        ids or skale.nodes.get_active_node_ids(),
    )
    for node_id in active_ids:
        if skale.nodes.get(node_id):
            skale.nodes.init_exit(node_id)
            skale.manager.node_exit(node_id)


def cleanup_schains(skale: SkaleManager) -> None:
    for schain_id in skale.schains_internal.get_all_schains_ids():
        schain_data = skale.schains.get(schain_id)
        schain_name = schain_data.name
        if schain_name is not None:
            skale.manager.delete_schain_by_root(schain_name, wait_for=True)


def cleanup_nodes_schains(skale: SkaleManager) -> None:
    print('Cleanup nodes and schains')
    cleanup_schains(skale)
    cleanup_nodes(skale)


def create_clean_schain(skale: SkaleManager) -> str:
    cleanup_nodes_schains(skale)
    create_nodes([skale])
    return create_schain(skale, random_name=True)


def create_node(skale: SkaleManager) -> str:
    cleanup_nodes_schains(skale)
    ip, public_ip, port, name = generate_random_node_data()
    skale.manager.create_node(
        ip=ip,
        port=port,
        name=name,
        domain_name=DEFAULT_DOMAIN_NAME,
        public_ip=public_ip,
        wait_for=True,
    )
    return name


def validator_exist(skale: SkaleManager) -> bool:
    return skale.validator_service.validator_address_exists(skale.wallet.address)


def add_delegation_period(skale: SkaleManager) -> None:
    is_added = skale.delegation_period_manager.is_delegation_period_allowed(D_DELEGATION_PERIOD)
    if not is_added:
        skale.delegation_period_manager.set_delegation_period(
            months_count=D_DELEGATION_PERIOD, stake_multiplier=D_STAKE_MULTIPLIER, wait_for=True
        )


def setup_validator(skale: SkaleManager) -> int:
    """Create and activate a validator"""
    set_test_msr(skale)
    print('Address', skale.wallet.address)
    if not validator_exist(skale):
        create_validator(skale)
    else:
        print('Skipping default validator creation')
    validator_id = skale.validator_service.validator_id_by_address(skale.wallet.address)
    if not skale.validator_service.get(validator_id)['trusted']:
        enable_validator(skale, validator_id)
    delegate_to_validator(skale, validator_id)
    delegations = skale.delegation_controller.get_all_delegations_by_validator(validator_id)
    accept_pending_delegation(skale, delegations[-1]['id'])
    _skip_evm_time(skale.web3, MONTH_IN_SECONDS)
    return validator_id


def link_address_to_validator(skale: SkaleManager) -> None:
    print('Linking address to validator')
    signature = skale.validator_service.get_link_node_signature(D_VALIDATOR_ID)
    tx_res = skale.validator_service.link_node_address(
        node_address=skale.wallet.address, signature=signature, wait_for=True
    )
    tx_res.raise_for_status()


def link_nodes_to_validator(
    skale: SkaleManager,
    validator_id: ValidatorId,
    node_skale_objs: Tuple[SkaleManager] | None = None,
) -> None:
    print('Linking address to validator')
    node_skale_objs = node_skale_objs or (skale,)
    validator_id = validator_id or D_VALIDATOR_ID
    for node_skale in node_skale_objs:
        signature = node_skale.validator_service.get_link_node_signature(validator_id)
        skale.validator_service.link_node_address(
            node_address=node_skale.wallet.address, signature=signature
        )


def skip_delegation_delay(skale: SkaleManager, delegation_id: int) -> None:
    print(f'Activating delegation with ID {delegation_id}')
    skale.token_state._skip_transition_delay(delegation_id, wait_for=True)


def accept_pending_delegation(skale: SkaleManager, delegation_id: int) -> None:
    print(f'Accepting delegation with ID: {delegation_id}')
    skale.delegation_controller.accept_pending_delegation(
        delegation_id=delegation_id, wait_for=True
    )


def get_test_delegation_amount(skale: SkaleManager) -> int:
    msr = skale.constants_holder.msr()
    return msr * 30


def set_test_msr(skale: SkaleManager, msr: int = D_VALIDATOR_MIN_DEL) -> None:
    skale.constants_holder._set_msr(new_msr=msr, wait_for=True)


def set_test_mda(skale: SkaleManager) -> None:
    skale.validator_service.set_validator_mda(0, wait_for=True)


def delegate_to_validator(skale: SkaleManager, validator_id: int = D_VALIDATOR_ID) -> None:
    print(f'Delegating tokens to validator ID: {validator_id}')
    skale.delegation_controller.delegate(
        validator_id=validator_id,
        amount=get_test_delegation_amount(skale),
        delegation_period=INITIAL_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        wait_for=True,
    )


def enable_validator(skale: SkaleManager, validator_id: int = D_VALIDATOR_ID) -> None:
    print(f'Enabling validator ID: {D_VALIDATOR_ID}')
    skale.validator_service._enable_validator(validator_id, wait_for=True)


def create_validator(skale: SkaleManager) -> None:
    print('Creating default validator')
    skale.validator_service.register_validator(
        name=D_VALIDATOR_NAME,
        description=D_VALIDATOR_DESC,
        fee_rate=D_VALIDATOR_FEE,
        min_delegation_amount=D_VALIDATOR_MIN_DEL,
        wait_for=True,
    )


def create_nodes(skales: List[SkaleManager], names: List[str] | None = None) -> list[int]:
    # create couple of nodes
    print('Creating two nodes')
    node_names = names or (DEFAULT_NODE_NAME, SECOND_NODE_NAME)
    for skale, name in zip(skales, node_names):
        ip, public_ip, port, _ = generate_random_node_data()
        skale.manager.create_node(
            ip=ip,
            port=port,
            name=name,
            domain_name=DEFAULT_DOMAIN_NAME,
            public_ip=public_ip,
            wait_for=True,
        )
    ids = [skales[0].nodes.node_name_to_index(name) for name in node_names]
    return ids


def create_schain(
    skale: SkaleManager,
    schain_name: SchainName = DEFAULT_SCHAIN_NAME,
    schain_type: int = 1,
    random_name: bool = False,
    schain_options: SchainOptions | None = None,
) -> str:
    print('Creating schain')
    # create 1 s-chain
    type_of_nodes, lifetime_seconds, name = generate_random_schain_data(skale)

    if random_name:
        schain_name = name

    if not schain_type:
        schain_type = type_of_nodes

    skale.schains.add_schain_by_foundation(
        lifetime_seconds,
        schain_type,
        0,
        schain_name,
        options=schain_options,
        wait_for=True,
        value=TEST_SRW_FUND_VALUE,
    )
    return schain_name
