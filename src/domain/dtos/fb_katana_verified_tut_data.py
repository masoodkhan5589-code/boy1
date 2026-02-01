from dataclasses import dataclass

from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.setting_loader_data import SettingLoaderData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData


@dataclass
class FbKatanaVerifiedTutData:
    id_source: str
    fb_access_token: str
    device_id: str
    settings: SettingLoaderData
    proxy_data: ProxyPayloadData
    virtual_device_info_data: VirtualDeviceInfoData
