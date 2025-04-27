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

from skale_contracts.projects.ima import SchainImaContract
from skale_contracts.project_factory import SkaleProject

from skale.skale_base import SkaleBase
from skale.contracts.ima.schain.message_proxy_for_schain import MessageProxyForSchain
from skale.contracts.ima.schain.token_manager_linker import TokenManagerLinker
from skale.contracts.ima.schain.token_manager_eth import TokenManagerETH
from skale.contracts.ima.schain.token_manager_erc20 import TokenManagerERC20
from skale.contracts.ima.schain.token_manager_erc721 import TokenManagerERC721
from skale.contracts.ima.schain.token_manager_erc721_wmt import (
    TokenManagerERC721WithMetadata,
)
from skale.contracts.ima.schain.token_manager_erc1155 import TokenManagerERC1155
from skale.contracts.ima.schain.community_locker import CommunityLocker


class SchainIma(SkaleBase):
    @property
    def project_name(self) -> SkaleProject:
        return SkaleProject.SCHAIN_IMA

    @cached_property
    def message_proxy_for_schain(self) -> MessageProxyForSchain:
        return MessageProxyForSchain(self, SchainImaContract.MESSAGE_PROXY_FOR_SCHAIN)

    @cached_property
    def community_locker(self) -> CommunityLocker:
        return CommunityLocker(self, SchainImaContract.COMMUNITY_LOCKER)

    @cached_property
    def token_manager_eth(self) -> TokenManagerETH:
        return TokenManagerETH(self, SchainImaContract.TOKEN_MANAGER_ETH)

    @cached_property
    def token_manager_erc20(self) -> TokenManagerERC20:
        return TokenManagerERC20(self, SchainImaContract.TOKEN_MANAGER_ERC20)

    @cached_property
    def token_manager_erc721(self) -> TokenManagerERC721:
        return TokenManagerERC721(self, SchainImaContract.TOKEN_MANAGER_ERC721)

    @cached_property
    def token_manager_erc721_wmt(self) -> TokenManagerERC721WithMetadata:
        return TokenManagerERC721WithMetadata(
            self, SchainImaContract.TOKEN_MANAGER_ERC721_WITH_META
        )

    @cached_property
    def token_manager_erc1155(self) -> TokenManagerERC1155:
        return TokenManagerERC1155(self, SchainImaContract.TOKEN_MANAGER_ERC1155)

    @cached_property
    def token_manager_linker(self) -> TokenManagerLinker:
        return TokenManagerLinker(self, SchainImaContract.TOKEN_MANAGER_LINKER)


def spawn_skale_ima_lib(schain_ima: SchainIma) -> SchainIma:
    """Clone skale ima object with the same wallet"""
    return SchainIma(schain_ima._endpoint, schain_ima.instance.address, schain_ima.wallet)
