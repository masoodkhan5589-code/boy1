from dataclasses import dataclass

from src.common.status_constants import StatusConstants
from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.setting_loader_data import SettingLoaderData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData


@dataclass
class FbKatanaVerifyAccountPayload:
    id_source: str
    fb_user_id: str
    fb_password: str
    device_id: str
    status_manager: StatusConstants
    proxy_payload_data: ProxyPayloadData
    settings: SettingLoaderData
    virtual_device_info_data: VirtualDeviceInfoData
