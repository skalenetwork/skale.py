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


class CurrentNodeInfo(NodeInfo):
    def __init__(self, node_id, node_name, base_port, bind_ip, ima_mainnet=None,
                 ima_mp_schain=None, ima_mp_mainnet=None, wallets=None, rotate_after_block=64,
                 schain_log_level='info', schain_log_level_config='info'):
        self.bind_ip = bind_ip
        self.schain_log_level = schain_log_level
        self.schain_log_level_config = schain_log_level_config

        self.ima_mainnet = ima_mainnet
        self.ima_mp_schain = ima_mp_schain
        self.ima_mp_mainnet = ima_mp_mainnet
        self.wallets = wallets

        self.rotate_after_block = rotate_after_block
        super().__init__(node_id, node_name, base_port)

    def to_config(self):
        config = super().to_config()
        config['bindIP'] = self.bind_ip
        config['logLevel'] = self.schain_log_level
        config['logLevelConfig'] = self.schain_log_level_config

        config['imaMainNet'] = self.ima_mainnet
        config['imaMessageProxySChain'] = self.ima_mp_schain
        config['imaMessageProxyMainNet'] = self.ima_mp_mainnet
        config['wallets'] = self.wallets

        config['rotateAfterBlock'] = self.rotate_after_block
        return config
