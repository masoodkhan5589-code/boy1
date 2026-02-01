from typing import Optional
from dataclasses import dataclass

from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.otp_service_response import OTPServiceResponse
from src.domain.dtos.base_fb_account_infomation_data import BaseFbAccountInformationData
from src.domain.dtos.virtual_device_chrome_info_data import VirtualDeviceChromeInfoData


@dataclass
class FbChromeCreatorWwwRequestData:
    id_source: str
    virtual_device_info_data: VirtualDeviceChromeInfoData
    fb_account_information_data: BaseFbAccountInformationData
    proxy_payload_data: ProxyPayloadData
    otp_service_response_data: Optional[OTPServiceResponse] = None
    response_to_table_widget: Optional[callable] = None
    additional_value: Optional[str] = None
