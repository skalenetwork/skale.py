NODE_DEPOSIT = 100000000000000000000

GAS = {
    'add_validator': 4500000,
    'create_node': 4500000,
    'create_schain': 7500000,
    'get_bounty': 4500000,
    'send_verdict': 200000,
    'set_check_time': 200000,
    'set_latency': 200000,
    'token_transfer': 600000,
    'add_authorized': 100000,
    'set_periods': 200000,
    'delete_node': 6000000,
    'delete_node_by_root': 6000000,
    'delete_schain': 6000000
}

OP_TYPES = {'create_node': 0x1, 'create_schain': 0x10}

LONG_LINE = '=' * 100

SCHAIN_TYPES = {
    'tiny': 1,
    'small': 2,
    'medium': 3,
    'test': 4,
}
