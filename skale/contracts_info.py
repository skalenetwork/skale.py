import skale.contracts as contracts
from skale.utils.contract_info import ContractInfo
from skale.utils.contract_types import ContractTypes

CONTRACTS_INFO = [
    ContractInfo('contract_manager', 'ContractManager',
                 contracts.ContractManager, ContractTypes.API, False),
    ContractInfo('token', 'SkaleToken', contracts.Token, ContractTypes.API,
                 False),
    ContractInfo('manager', 'SkaleManager', contracts.Manager,
                 ContractTypes.API, False),
    ContractInfo('constants', 'Constants', contracts.Constants,
                 ContractTypes.INTERNAL, True),
    ContractInfo('nodes', 'NodesFunctionality', contracts.Nodes,
                 ContractTypes.API, True),
    ContractInfo('schains', 'SchainsFunctionality', contracts.SChains,
                 ContractTypes.API, True),
    ContractInfo('validators', 'ValidatorsFunctionality', contracts.Validators,
                 ContractTypes.API, True),
    ContractInfo('nodes_data', 'NodesData', contracts.NodesData,
                 ContractTypes.DATA, True),
    ContractInfo('schains_data', 'SchainsData', contracts.SChainsData,
                 ContractTypes.DATA, True),
    ContractInfo('validators_data', 'ValidatorsData', contracts.ValidatorsData,
                 ContractTypes.DATA, True)
]
