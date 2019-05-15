from skale.utils.node_info import NodeInfo


class CurrentNodeInfo(NodeInfo):
    def __init__(self, node_id, node_name, base_port, bind_ip):
        self.bind_ip = bind_ip
        super().__init__(node_id, node_name, base_port)

    def to_config(self):
        return {**super().to_config(), **{
            'bindIP': self.bind_ip
        }}
