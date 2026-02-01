from typing import Optional
from dataclasses import dataclass

from src.common.status_constants import StatusConstants
from src.domain.dtos.base_fb_account_infomation_data import BaseFbAccountInformationData
from src.domain.dtos.global_config_data import GlobalConfigData
from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData


@dataclass
class FbCreatorAppRequestMainData:
    id_source: str
    virtual_device_info_data: VirtualDeviceInfoData
    status_manager_instance: StatusConstants
    fb_account_information_data: BaseFbAccountInformationData
    proxy_payload_data: ProxyPayloadData
    global_config_data: GlobalConfigData
    temporary_contact: Optional[str] = None
    response_to_table_widget: Optional[callable] = None
