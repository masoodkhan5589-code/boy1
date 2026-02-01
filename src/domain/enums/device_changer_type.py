from enum import Enum
from collections import namedtuple

DeviceChangerInfo = namedtuple('DeviceChangerInfo', ['key', 'label'])


class DeviceChangerType(Enum):
    DISABLED = DeviceChangerInfo('disabled', 'Disabled')
    REBOOT = DeviceChangerInfo('reboot', 'Reboot (Room changer)')
    TLC_HELPER = DeviceChangerInfo('tlc_helper', 'TLC Helper')
    MI_CHANGER = DeviceChangerInfo('mi_changer', 'MiChanger')
