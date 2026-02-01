from abc import ABC, abstractmethod
from src.domain.dtos.otp_service_response import OTPServiceResponse


class IContactManager(ABC):

    @abstractmethod
    def get_contact(self, **kwargs) -> OTPServiceResponse:
        ...

    @abstractmethod
    def get_otp(self, otp_service_response: OTPServiceResponse) -> str:
        ...
