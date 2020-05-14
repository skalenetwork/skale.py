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

from web3 import Web3

from skale.dataclasses import CurrentNodeInfo, SchainNodeInfo
from skale.schain_config.ports_allocation import get_schain_base_port_on_node
from skale.schain_config import PRECOMPILED_IMA_CONTRACTS
from skale.utils.helper import ip_from_bytes, decapitalize
from skale.utils.web3_utils import public_key_to_address
from skale.schain_config.base_config import update_base_config


def generate_schain_info(schain, schain_nodes, storage_limit,
                         snapshot_interval_ms=None,
                         empty_block_interval_ms=None):
    schain_info = {
        'schainID': 1,  # todo: remove this later (should be removed from the skaled first)
        'schainName': schain['name'],
        'schainOwner': schain['owner'],
        'nodes': schain_nodes,
        'storageLimit': storage_limit
    }
    if snapshot_interval_ms:
        schain_info['snapshotIntervalMs'] = snapshot_interval_ms
    if empty_block_interval_ms:
        schain_info['emptyBlockIntervalMs'] = empty_block_interval_ms
    return schain_info


def get_nodes_for_schain(skale, name):
    nodes = []
    ids = skale.schains_data.get_node_ids_for_schain(name)
    for id_ in ids:
        node = skale.nodes_data.get(id_)
        node['id'] = id_
        nodes.append(node)
    return nodes


def get_nodes_for_schain_config(skale, name):
    nodes_info = []
    nodes = get_nodes_for_schain(skale, name)
    for i, node in enumerate(nodes, 1):
        pk = node['publicKey'].hex()

        schains_on_node = skale.schains_data.get_schains_for_node(node['id'])
        base_port = get_schain_base_port_on_node(schains_on_node, name, node['port'])

        node_info = SchainNodeInfo(
            node_name=node['name'],
            node_id=node['id'],
            base_port=base_port,

            schain_index=i,
            ip=ip_from_bytes(node['ip']),
            public_key=pk,
            public_ip=ip_from_bytes(node['publicIP']),
            owner=public_key_to_address(pk)
        ).to_config()
        nodes_info.append(node_info)
    return nodes_info


def get_contract_address_from_ima_data(ima_data, name):
    return ima_data[f'{name}_address']


def generate_permitted_ima_contracts_info(ima_data):
    permitted_contracts = {}
    for name in PRECOMPILED_IMA_CONTRACTS:
        contract_filename = PRECOMPILED_IMA_CONTRACTS[name]['filename']
        permitted_contracts[contract_filename] = get_contract_address_from_ima_data(ima_data, name)
    return permitted_contracts


def generate_mp_authorized_callers(ima_data, schain_owner, schain_nodes):
    mp_authorized_callers = {}
    for name in PRECOMPILED_IMA_CONTRACTS:
        address = get_contract_address_from_ima_data(ima_data, name)
        mp_authorized_callers[address] = 1
    for node in schain_nodes:
        acc_fx = Web3.toChecksumAddress(node['owner'])
        if not mp_authorized_callers.get(acc_fx, None):
            mp_authorized_callers[acc_fx] = 1
    schain_owner_fx = Web3.toChecksumAddress(schain_owner)
    if not mp_authorized_callers.get(schain_owner_fx, None):
        mp_authorized_callers[schain_owner_fx] = 1
    return mp_authorized_callers


def generate_ima_contracts_addresses(ima_data):
    ima_contracts_addresses = {}
    for name in PRECOMPILED_IMA_CONTRACTS:
        contract_filename = PRECOMPILED_IMA_CONTRACTS[name]['filename']
        address = get_contract_address_from_ima_data(ima_data, name)
        ima_contracts_addresses[decapitalize(contract_filename)] = address
    return ima_contracts_addresses


def generate_schain_contract_settings(ima_data, schain_owner, schain_nodes):
    # todo: refactor
    permitted_contracts = generate_permitted_ima_contracts_info(ima_data)
    mp_authorized_callers = generate_mp_authorized_callers(ima_data, schain_owner, schain_nodes)
    ima_contracts_addresses = generate_ima_contracts_addresses(ima_data)
    return {
        'common': {
            'enableContractLogMessages': False
        },
        'IMA': {
            'ownerAddress': schain_owner,
            'variables': {
                'LockAndDataForSchain': {
                    'permitted': permitted_contracts
                },
                'MessageProxyForSchain': {
                    'mapAuthorizedCallers': mp_authorized_callers
                }
            },
            **ima_contracts_addresses
        }
    }


def generate_schain_config(base_config, node_info, schain_info, schain_contract_settings={}):
    return {
        **base_config,
        'skaleConfig': {
            'contractSettings': schain_contract_settings,
            'nodeInfo': node_info,
            'sChain': schain_info,
        }
    }


def generate_skale_schain_config(skale, schain_name, node_id, base_config=None, ima_mainnet=None,
                                 ima_mp_schain=None, ima_mp_mainnet=None, wallets=None,
                                 ima_data=None, rotate_after_block=64, storage_limit=1000000000,
                                 empty_block_interval_ms=None, snapshot_interval_ms=None,
                                 schain_log_level='info', schain_log_level_config='info'):
    node = skale.nodes_data.get(node_id)
    schain = skale.schains_data.get_by_name(schain_name)

    schains_on_node = skale.schains_data.get_schains_for_node(node_id)
    schain_base_port_on_node = get_schain_base_port_on_node(schains_on_node, schain_name,
                                                            node['port'])
    schain_nodes = get_nodes_for_schain_config(skale, schain_name)

    node_info = CurrentNodeInfo(
        node_name=node['name'],
        node_id=node_id,
        base_port=schain_base_port_on_node,
        bind_ip=ip_from_bytes(node['ip']),
        ima_mainnet=ima_mainnet,
        ima_mp_schain=ima_mp_schain,
        ima_mp_mainnet=ima_mp_mainnet,
        wallets=wallets,
        rotate_after_block=rotate_after_block,
        schain_log_level=schain_log_level,
        schain_log_level_config=schain_log_level_config
    ).to_config()

    schain_info = generate_schain_info(
        schain=schain,
        schain_nodes=schain_nodes,
        storage_limit=storage_limit,
        empty_block_interval_ms=empty_block_interval_ms,
        snapshot_interval_ms=snapshot_interval_ms
    )

    if base_config:
        update_base_config(base_config, schain, schain_nodes, ima_data=ima_data)
    else:
        base_config = {}
    if ima_data:
        schain_contract_settings = generate_schain_contract_settings(ima_data, schain['owner'],
                                                                     schain_nodes)
    else:
        schain_contract_settings = {}
    return generate_schain_config(
        base_config=base_config,
        node_info=node_info,
        schain_info=schain_info,
        schain_contract_settings=schain_contract_settings
    )
