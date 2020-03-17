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

from skale.dataclasses.node_info import NodeInfo


class SchainNodeInfo(NodeInfo):
    def __init__(self, node_id, node_name, base_port, public_key, owner, schain_index, ip,
                 public_ip):
        self.public_key = public_key
        self.owner = owner
        self.schain_index = schain_index
        self.ip = ip
        self.public_ip = public_ip
        super().__init__(node_id, node_name, base_port)

    def to_config(self):
        return {**super().to_config(), **{
            'publicKey': self.public_key,
            'owner': self.owner,
            'schainIndex': self.schain_index,
            'ip': self.ip,
            'publicIP': self.public_ip
        }}
