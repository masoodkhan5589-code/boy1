from abc import ABC, abstractmethod
from typing import Union, Literal

from src.domain.dtos.instagram_virtual_device_info_data import InstagramVirtualDeviceInfoData
from src.domain.dtos.virtual_device_chrome_info_data import VirtualDeviceChromeInfoData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData


class IDeviceInfoGenerator(ABC):
    @abstractmethod
    def generate(
            self,
            country_code: str = None,
            app_type: Literal["facebook", "instagram"] = "facebook"
    ) -> Union[VirtualDeviceChromeInfoData, VirtualDeviceInfoData, InstagramVirtualDeviceInfoData]:
        ...
