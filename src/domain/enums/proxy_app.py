from collections import namedtuple
from enum import Enum

ProxyAppInfo = namedtuple('ProxyAppInfo', ['key', 'label'])


class ProxyApp(Enum):
    DISABLED = ProxyAppInfo("disabled", "Disable")
    ENABLE = ProxyAppInfo("enable", "Enable")
