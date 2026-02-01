from dataclasses import dataclass

from src.common.status_constants import StatusConstants
from src.domain.dtos.base_fb_account_infomation_data import BaseFbAccountInformationData
from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData


@dataclass
class FbKatanaCreatorRequestData:
    id_source: str
    device_id: str
    virtual_device_info_data: VirtualDeviceInfoData
    fb_account_information_data: BaseFbAccountInformationData
    proxy_payload_data: ProxyPayloadData
    status_manager_instance: StatusConstants
