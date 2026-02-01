from dataclasses import dataclass

from src.common.status_constants import StatusConstants
from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.setting_loader_data import SettingLoaderData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData


@dataclass
class FbKatanaEnableTwoFactorData:
    id_source: str
    virtual_device_info_data: VirtualDeviceInfoData
    status_manager_instance: StatusConstants
    settings: SettingLoaderData
    proxy_payload_data: ProxyPayloadData
    response_to_table_widget: callable
