from enum import IntEnum

NODE_DEPOSIT = 100000000000000000000

GAS = {
    'add_validator': 4500000,
    'create_node': 4500000,
    'create_schain': 7500000,
    'get_bounty': 4500000,
    'send_verdict': 200000,
    'set_check_time': 200000,
    'set_latency': 200000,
    'token_transfer': 60000,
    'add_authorized': 100000,
    'set_periods': 200000,
    'delete_node': 600000,
    'delete_node_by_root': 600000,
    'delete_schain': 600000
}

OP_TYPES = {'create_node': 0x1, 'create_schain': 0x10}

LONG_LINE = '=' * 100


class SchainType(IntEnum):
    TINY = 1
    SMALL = 2
    MEDIUM = 3
    TEST2 = 4
    TEST4 = 5
