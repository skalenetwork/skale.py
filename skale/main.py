import logging

from web3 import Web3, WebsocketProvider

import skale.contracts as contracts
from skale.blockchain_env import BlockchainEnv
from skale.contracts_info import CONTRACTS_INFO
from skale.utils.helper import (generate_custom_config, generate_ws_addr,
                                get_abi, load_skale_env_config)

logger = logging.getLogger(__name__)


class Skale:
    def __init__(self, skale_env, ip=None, ws_port=None, abi_filepath=None):
        if (ip and ws_port):
            env_config = generate_custom_config(ip, ws_port)
        else:
            env_config = load_skale_env_config(skale_env)

        logger.info(
            f'Init skale-py: skale_env: {skale_env}, env_config: {env_config}')
        ws_addr = generate_ws_addr(env_config['ip'], env_config['ws_port'])
        self.web3 = Web3(WebsocketProvider(ws_addr))
        self.abi = get_abi(skale_env, abi_filepath)
        self.__contracts = {}
        self.__contracts_info = {}
        self.nonces = {}

        self.__init_contracts_info()
        self.__init_contracts()

    def __init_contracts_info(self):
        for contract_info in CONTRACTS_INFO:
            self.__add_contract_info(contract_info)

    def __add_contract_info(self, contract_info):
        self.__contracts_info[contract_info.name] = contract_info

    def __init_contracts(self):
        self.add_lib_contract('contract_manager', contracts.ContractManager)
        for name in self.__contracts_info:
            info = self.__contracts_info[name]
            if info.upgradable:
                self.init_upgradable_contract(info)
            else:
                self.add_lib_contract(info.name, info.contract_class)

    def init_upgradable_contract(self, contract_info):
        address = self.get_contract_address(contract_info.contract_name)
        self.add_lib_contract(contract_info.name, contract_info.contract_class,
                              address)

    def add_lib_contract(self, name, contract_class, contract_address=None):
        address = contract_address or self.get_contract_addres_by_name(
            self.abi, name)
        abi = self.get_contract_abi_by_name(self.abi, name)
        self.add_contract(name, contract_class(self, name, address, abi))

    def get_contract_addres_by_name(self, abi, name):
        return abi.get(f'skale_{name}_address') or abi.get(f'{name}_address')

    def get_contract_abi_by_name(self, abi, name):  # todo: unify abi key names
        return abi.get(f'skale_{name}_abi') or abi.get(
            f'{name}_abi') or abi.get(f'{name}_functionality_abi') or abi.get(
            f'{name}_data_abi')

    def add_contract(self, name, skale_contract):
        logger.debug(f'Init contract: {name}')
        self.__contracts[name] = skale_contract

    def get_contract_address(self, name):
        return self.contract_manager.get_contract_address(name)

    def get_contract_by_name(self, name):
        return self.__contracts[name]

    def __getattr__(self, name):
        if name not in self.__contracts:
            raise AttributeError(name)
        return self.get_contract_by_name(name)
