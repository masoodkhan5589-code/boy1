from abc import ABC, abstractmethod
from typing import Optional, Union

from src.domain.dtos.otp_service_response import OTPServiceResponse


class IOtpService(ABC):

    @abstractmethod
    def get_balance(self) -> Union[int, str, None]:
        pass

    @abstractmethod
    def create(self, max_attempts: int = 5, **kwargs) -> tuple[any, Optional[OTPServiceResponse]]:
        pass

    @abstractmethod
    def get_code(self, **kwargs) -> Union[str, None]:
        pass
