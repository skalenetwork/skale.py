from enum import Enum


class BlockchainEnv(Enum):
    UA_SERVER = 'ua_server'
    AWS = 'aws'
    AWS2 = 'aws2'
    AWS3 = 'aws3'
    LOCAL = 'local'
    CUSTOM = 'custom'
    DO = 'do'
    TEST = 'test'
