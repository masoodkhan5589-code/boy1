from abc import ABC, abstractmethod

from src.domain.dtos.check_info_token_response_data import CheckInfoTokenResponseData


class IFbChecker(ABC):

    @staticmethod
    @abstractmethod
    def check_uid(fb_uid: str) -> bool:
        ...

    @abstractmethod
    def check_token(self, fb_uid: str, fb_access_token: str) -> CheckInfoTokenResponseData:
        ...
