from dataclasses import dataclass

from src.domain.dtos.instagram_virtual_device_info_data import InstagramVirtualDeviceInfoData
from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.setting_loader_data import SettingLoaderData


@dataclass
class IGBaseUpdateInfoData:
    id_source: str
    virtual_device_info_data: InstagramVirtualDeviceInfoData
    settings: SettingLoaderData
    proxy_payload_data: ProxyPayloadData
