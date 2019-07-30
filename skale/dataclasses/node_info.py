from skale.skaled_ports import SkaledPorts


class NodeInfo():
    def __init__(self, node_id, node_name, base_port):
        self.node_id = node_id
        self.node_name = node_name
        self.base_port = base_port
        self.calc_ports()

    def calc_ports(self):
        self.http_rpc_port = self.base_port + SkaledPorts.HTTP_JSON.value
        self.https_rpc_port = self.base_port + SkaledPorts.HTTPS_JSON.value
        self.ws_rpc_port = self.base_port + SkaledPorts.WS_JSON.value
        self.wss_rpc_port = self.base_port + SkaledPorts.WSS_JSON.value

    def to_config(self):
        return {
            'nodeID': self.node_id,
            'nodeName': self.node_name,
            'basePort': self.base_port,
            'httpRpcPort': self.http_rpc_port,
            'httpsRpcPort': self.https_rpc_port,
            'wsRpcPort': self.ws_rpc_port,
            'wssRpcPort': self.wss_rpc_port
        }
