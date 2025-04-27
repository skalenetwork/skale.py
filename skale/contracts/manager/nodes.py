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
"""Nodes.sol functions"""

import socket
from typing import Any, Dict, List, Tuple, cast

from Crypto.Hash import keccak
from eth_typing import BlockNumber, ChecksumAddress
from web3.contract.contract import ContractFunction
from web3.exceptions import BadFunctionCallOutput, ContractLogicError

from skale.contracts.base_contract import transaction_method

from skale.contracts.skale_manager_contract import SkaleManagerContract
from skale.types.node import Node, NodeId, NodeStatus, Port
from skale.types.validator import ValidatorId
from skale.utils.exceptions import InvalidNodeIdError
from skale.utils.helper import format_fields

FIELDS = [
    'name',
    'ip',
    'publicIP',
    'port',
    'start_block',
    'last_reward_date',
    'finish_time',
    'status',
    'validator_id',
    'publicKey',
    'domain_name',
]


class Nodes(SkaleManagerContract):
    def __get_raw(self, node_id: NodeId) -> List[Any]:
        try:
            return list(self.contract.functions.nodes(node_id).call())
        except (ContractLogicError, ValueError, BadFunctionCallOutput):
            raise InvalidNodeIdError(node_id)

    def __get_raw_w_pk(self, node_id: NodeId) -> List[Any]:
        raw_node_struct = self.__get_raw(node_id)
        raw_node_struct.append(self.get_node_public_key(node_id))
        return raw_node_struct

    def __get_raw_w_pk_w_domain(self, node_id: NodeId) -> List[Any]:
        raw_node_struct_w_pk = self.__get_raw_w_pk(node_id)
        raw_node_struct_w_pk.append(self.get_domain_name(node_id))
        return raw_node_struct_w_pk

    @format_fields(FIELDS)
    def untyped_get(self, node_id: NodeId) -> List[Any]:
        return self.__get_raw_w_pk_w_domain(node_id)

    def get(self, node_id: NodeId) -> Node:
        node = self.untyped_get(node_id)
        if node is None:
            raise ValueError('Node with id ', node_id, ' is not found')
        if isinstance(node, dict):
            return self._to_node(node)
        if isinstance(node, list):
            return self._to_node(node[0])
        raise ValueError("Can't process returned node type")

    @format_fields(FIELDS)
    def get_by_name(self, name: str) -> List[Any]:
        name_hash = self.name_to_id(name)
        _id = self.contract.functions.nodesNameToIndex(name_hash).call()
        return self.__get_raw_w_pk_w_domain(_id)

    def get_nodes_number(self) -> int:
        return int(self.contract.functions.getNumberOfNodes().call())

    def get_active_node_ids(self) -> List[NodeId]:
        nodes_number = self.get_nodes_number()
        return [
            NodeId(node_id)
            for node_id in range(0, nodes_number)
            if self.get_node_status(NodeId(node_id)) == NodeStatus.ACTIVE
        ]

    def get_active_node_ips(self) -> List[bytes]:
        nodes_number = self.get_nodes_number()
        return [
            self.get(NodeId(node_id))['ip']
            for node_id in range(0, nodes_number)
            if self.get_node_status(NodeId(node_id)) == NodeStatus.ACTIVE
        ]

    def name_to_id(self, name: str) -> bytes:
        keccak_hash = keccak.new(data=name.encode('utf8'), digest_bits=256)
        return keccak_hash.digest()

    def is_node_name_available(self, name: str) -> bool:
        node_id = self.name_to_id(name)
        return not self.contract.functions.nodesNameCheck(node_id).call()

    def is_node_ip_available(self, ip: str) -> bool:
        ip_bytes = socket.inet_aton(ip)
        return not self.contract.functions.nodesIPCheck(ip_bytes).call()

    def node_name_to_index(self, name: str) -> int:
        name_hash = self.name_to_id(name)
        return int(self.contract.functions.nodesNameToIndex(name_hash).call())

    def get_node_status(self, node_id: NodeId) -> NodeStatus:
        try:
            return NodeStatus(self.contract.functions.getNodeStatus(node_id).call())
        except (ContractLogicError, ValueError, BadFunctionCallOutput):
            raise InvalidNodeIdError(node_id)

    def get_node_finish_time(self, node_id: NodeId) -> int:
        try:
            return int(self.contract.functions.getNodeFinishTime(node_id).call())
        except (ContractLogicError, ValueError, BadFunctionCallOutput):
            raise InvalidNodeIdError(node_id)

    def __get_node_public_key_raw(self, node_id: NodeId) -> Tuple[bytes, bytes]:
        try:
            return cast(
                Tuple[bytes, bytes], self.contract.functions.getNodePublicKey(node_id).call()
            )
        except (ContractLogicError, ValueError, BadFunctionCallOutput):
            raise InvalidNodeIdError(node_id)

    def get_node_public_key(self, node_id: NodeId) -> str:
        raw_key = self.__get_node_public_key_raw(node_id)
        key_bytes = raw_key[0] + raw_key[1]
        return self.skale.web3.to_hex(key_bytes)

    def get_validator_node_indices(self, validator_id: int) -> list[NodeId]:
        """Returns list of node indices to the validator

        :returns: List of trusted node indices
        :rtype: list
        """
        return [
            NodeId(id)
            for id in self.contract.functions.getValidatorNodeIndexes(validator_id).call()
        ]

    def get_last_change_ip_time(self, node_id: NodeId) -> int:
        return int(self.contract.functions.getLastChangeIpTime(node_id).call())

    @transaction_method
    def set_node_in_maintenance(self, node_id: NodeId) -> 'ContractFunction':
        return self.contract.functions.setNodeInMaintenance(node_id)

    @transaction_method
    def remove_node_from_in_maintenance(self, node_id: NodeId) -> 'ContractFunction':
        return self.contract.functions.removeNodeFromInMaintenance(node_id)

    @transaction_method
    def set_domain_name(self, node_id: NodeId, domain_name: str) -> 'ContractFunction':
        return self.contract.functions.setDomainName(node_id, domain_name)

    def get_domain_name(self, node_id: NodeId) -> str:
        return str(self.contract.functions.getNodeDomainName(node_id).call())

    @transaction_method
    def grant_role(self, role: bytes, owner: ChecksumAddress) -> 'ContractFunction':
        return self.contract.functions.grantRole(role, owner)

    def has_role(self, role: bytes, address: ChecksumAddress) -> bool:
        return bool(self.contract.functions.hasRole(role, address).call())

    def node_manager_role(self) -> bytes:
        return bytes(self.contract.functions.NODE_MANAGER_ROLE().call())

    def compliance_role(self) -> bytes:
        return bytes(self.contract.functions.COMPLIANCE_ROLE().call())

    @transaction_method
    def init_exit(self, node_id: NodeId) -> 'ContractFunction':
        return self.contract.functions.initExit(node_id)

    @transaction_method
    def change_ip(self, node_id: NodeId, ip: bytes, public_ip: bytes) -> 'ContractFunction':
        return self.contract.functions.changeIP(node_id, ip, public_ip)

    def _to_node(self, untyped_node: Dict[str, Any]) -> Node:
        for key in Node.__annotations__:
            if key not in untyped_node:
                raise ValueError(f'Key: {key} is not available in node.')
        return Node(
            {
                'name': str(untyped_node['name']),
                'ip': bytes(untyped_node['ip']),
                'publicIP': bytes(untyped_node['publicIP']),
                'port': Port(untyped_node['port']),
                'start_block': BlockNumber(untyped_node['start_block']),
                'last_reward_date': int(untyped_node['last_reward_date']),
                'finish_time': int(untyped_node['finish_time']),
                'status': NodeStatus(untyped_node['status']),
                'validator_id': ValidatorId(untyped_node['validator_id']),
                'publicKey': str(untyped_node['publicKey']),
                'domain_name': str(untyped_node['domain_name']),
            }
        )
