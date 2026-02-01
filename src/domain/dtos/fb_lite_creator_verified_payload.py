from dataclasses import dataclass

from src.common.status_constants import StatusConstants
from src.domain.dtos.base_fb_account_infomation_data import BaseFbAccountInformationData
from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.setting_loader_data import SettingLoaderData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData


@dataclass
class FbLiteCreatorVerifiedPayload:
    id_source: str
    device_id: str
    status_manager: StatusConstants
    fb_account_information_data: BaseFbAccountInformationData
    proxy_payload_data: ProxyPayloadData
    settings: SettingLoaderData
    virtual_device_info_data: VirtualDeviceInfoData
    response_to_table_widget: callable
    language: str = 'en'
