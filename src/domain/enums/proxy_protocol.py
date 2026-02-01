from enum import Enum


class ProxyProtocol(Enum):
    HTTPS = "HTTPS"
    HTTP = "HTTP"
    SOCKS5 = "SOCKS5"
