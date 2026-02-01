from dataclasses import dataclass

from src.common.status_constants import StatusConstants
from src.domain.dtos.global_config_data import GlobalConfigData
from src.domain.dtos.proxy_payload_data import ProxyPayloadData


@dataclass
class FbKatanaEnableTwoFactorMainData:
    id_source: str
    status_manager_instance: StatusConstants
    global_config_data: GlobalConfigData
    proxy_payload_data: ProxyPayloadData
    response_to_table_widget: callable
