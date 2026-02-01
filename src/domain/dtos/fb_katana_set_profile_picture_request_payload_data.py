from dataclasses import dataclass

from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData


@dataclass
class FbKatanaSetProfilePictureRequestPayloadData:
    proxy_payload_data: ProxyPayloadData
    virtual_device_info_data: VirtualDeviceInfoData
