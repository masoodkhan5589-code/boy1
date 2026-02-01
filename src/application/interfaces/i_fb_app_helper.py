from abc import ABC, abstractmethod
from typing import Dict, Any

from src.application.interfaces.i_contact_manager import IContactManager
from src.application.interfaces.i_proxy_manager import IProxyManager
from src.domain.dtos.otp_service_response import OTPServiceResponse
from src.common.status_constants import StatusConstants


class IFbAppHelper(ABC):
    """
    Interface cho lớp helper hỗ trợ các Use Case của Facebook.
    """

    @property
    @abstractmethod
    def id_source(self) -> str:
        pass

    @property
    @abstractmethod
    def proxies_manager_instance(self) -> IProxyManager:
        pass

    @property
    @abstractmethod
    def status_manager_instance(self) -> StatusConstants:
        pass

    @property
    @abstractmethod
    def primary_contact_management(self) -> IContactManager:
        pass

    @property
    @abstractmethod
    def secondary_contact_management(self) -> IContactManager:
        pass

    @property
    @abstractmethod
    def primary_otp_service_response(self) -> OTPServiceResponse:
        pass

    @primary_otp_service_response.setter
    @abstractmethod
    def primary_otp_service_response(self, value: OTPServiceResponse):
        pass

    @property
    @abstractmethod
    def secondary_otp_service_response(self) -> OTPServiceResponse:
        pass

    @secondary_otp_service_response.setter
    @abstractmethod
    def secondary_otp_service_response(self, value: OTPServiceResponse):
        pass

    @property
    @abstractmethod
    def result(self) -> Dict[str, Any]:
        pass

    @result.setter
    @abstractmethod
    def result(self, value: Dict[str, Any]):
        pass

    @property
    @abstractmethod
    def verified(self) -> bool:
        pass

    @property
    @abstractmethod
    def error(self) -> bool:
        pass

    @error.setter
    def error(self, value: bool):
        pass

    @verified.setter
    @abstractmethod
    def verified(self, value: bool):
        pass

    @property
    @abstractmethod
    def unverified(self) -> bool:
        pass

    @unverified.setter
    @abstractmethod
    def unverified(self, value: bool):
        pass

    @property
    @abstractmethod
    def try_again(self) -> bool:
        pass

    @try_again.setter
    @abstractmethod
    def try_again(self, value: bool):
        pass

    @property
    @abstractmethod
    def account_disabled(self) -> bool:
        pass

    @account_disabled.setter
    @abstractmethod
    def account_disabled(self, value: bool):
        pass

    @abstractmethod
    def check_live_account(self, check_info_token: bool = False) -> bool:
        pass

    @abstractmethod
    def update_status(self, success: bool = True, **kwargs) -> bool:
        pass

    @property
    @abstractmethod
    def reuse_old_contact(self) -> bool:
        pass

    @reuse_old_contact.setter
    @abstractmethod
    def reuse_old_contact(self, value: bool):
        pass
