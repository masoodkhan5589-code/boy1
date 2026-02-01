from dataclasses import dataclass

from src.common.status_constants import StatusConstants
from src.domain.dtos.global_config_data import GlobalConfigData
from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData


@dataclass
class FbKatanaGetTokenData:
    id_source: str
    facebook_user_id: str
    fb_access_token: str
    status_manager_instance: StatusConstants
    global_config_data: GlobalConfigData = None
    virtual_device_info_data: VirtualDeviceInfoData = None
    proxy_payload_data: ProxyPayloadData = None
    response_to_table_widget: callable = None
