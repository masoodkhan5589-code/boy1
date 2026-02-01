from dataclasses import dataclass


@dataclass
class VirtualDeviceChromeInfoData:
    user_agent: str
    x_asbd_id: str
    ri: str
