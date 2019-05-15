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
