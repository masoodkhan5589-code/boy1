from abc import ABC, abstractmethod
from typing import Optional

from src.domain.dtos.fb_katana_creator_request_data import FbKatanaCreatorRequestData
from src.domain.dtos.proxy_payload_data import ProxyPayloadData


class IFbKatanaCreatorRequest(ABC):

    @abstractmethod
    def __init__(self, payload: FbKatanaCreatorRequestData):
        pass

    @abstractmethod
    def password_key_fetch(self) -> bool:
        pass

    @abstractmethod
    def caa_reg_password_async(self, contact: str) -> bool:
        pass

    @abstractmethod
    def caa_reg_create_account_async(self, contact: str) -> tuple[bool, bool]:
        pass

    @abstractmethod
    def fetch_account_information(self) -> tuple[Optional[str], Optional[str], Optional[str], bool]:
        pass

    @abstractmethod
    def update_proxy(self, proxy_payload_data: ProxyPayloadData) -> None:
        pass

    @property
    @abstractmethod
    def payload(self) -> FbKatanaCreatorRequestData:
        pass
