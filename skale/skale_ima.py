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

from functools import cached_property

from skale_contracts.projects.ima import MainnetImaContract
from skale_contracts.project_factory import SkaleProject

from skale.skale_base import SkaleBase
from skale.contracts.ima.mainnet.message_proxy_for_mainnet import MessageProxyForMainnet
from skale.contracts.ima.mainnet.linker import Linker
from skale.contracts.ima.mainnet.community_pool import CommunityPool
from skale.contracts.ima.mainnet.deposit_box_eth import DepositBoxEth
from skale.contracts.ima.mainnet.deposit_box_erc20 import DepositBoxERC20
from skale.contracts.ima.mainnet.deposit_box_erc721 import DepositBoxERC721
from skale.contracts.ima.mainnet.deposit_box_erc721_wmt import (
    DepositBoxERC721WithMetadata,
)
from skale.contracts.ima.mainnet.deposit_box_erc1155 import DepositBoxERC1155


class SkaleIma(SkaleBase):
    @property
    def project_name(self) -> SkaleProject:
        return SkaleProject.MAINNET_IMA

    @cached_property
    def message_proxy_for_mainnet(self) -> MessageProxyForMainnet:
        return MessageProxyForMainnet(self, MainnetImaContract.MESSAGE_PROXY_FOR_MAINNET)

    @cached_property
    def linker(self) -> Linker:
        return Linker(self, MainnetImaContract.LINKER)

    @cached_property
    def community_pool(self) -> CommunityPool:
        return CommunityPool(self, MainnetImaContract.COMMUNITY_POOL)

    @cached_property
    def deposit_box_eth(self) -> DepositBoxEth:
        return DepositBoxEth(self, MainnetImaContract.DEPOSIT_BOX_ETH)

    @cached_property
    def deposit_box_erc20(self) -> DepositBoxERC20:
        return DepositBoxERC20(self, MainnetImaContract.DEPOSIT_BOX_ERC20)

    @cached_property
    def deposit_box_erc721(self) -> DepositBoxERC721:
        return DepositBoxERC721(self, MainnetImaContract.DEPOSIT_BOX_ERC721)

    @cached_property
    def deposit_box_erc721_wmt(self) -> DepositBoxERC721WithMetadata:
        return DepositBoxERC721WithMetadata(self, MainnetImaContract.DEPOSIT_BOX_ERC721_WMT)

    @cached_property
    def deposit_box_erc1155(self) -> DepositBoxERC1155:
        return DepositBoxERC1155(self, MainnetImaContract.DEPOSIT_BOX_ERC1155)


def spawn_skale_ima_lib(skale_ima: SkaleIma) -> SkaleIma:
    """Clone skale ima object with the same wallet"""
    return SkaleIma(skale_ima._endpoint, skale_ima.instance.address, skale_ima.wallet)
