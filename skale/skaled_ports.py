from enum import Enum


class SkaledPorts(Enum):
    PROPOSAL = 0
    CATCHUP = 1
    HTTP_JSON = 2
    WS_JSON = 3
    BINARY_CONSENSUS = 4
    ZMQ_BROADCAST = 5
    MTA = 6
    HTTPS_JSON = 7
    WSS_JSON = 8
