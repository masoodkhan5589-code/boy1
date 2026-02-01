from abc import ABC, abstractmethod
from typing import Tuple, Optional
import requests


class IFbChromeForgotPasswordRequest(ABC):

    HTTP_ENDPOINT = "https://www.facebook.com"

    @abstractmethod
    def get_facebook_page(self, session: requests.Session) -> Tuple[bool, requests.Session]:
        ...

    @abstractmethod
    def recover(self, contact: str, session: requests.Session) -> Tuple[bool, requests.Session]:
        ...

    @abstractmethod
    def get_redirect_page(self, session: requests.Session) -> Tuple[bool, requests.Session]:
        ...

    @abstractmethod
    def send_recovery_request(self, session: requests.Session) -> Tuple[bool, Optional[str], requests.Session]:
        ...

    @abstractmethod
    def confirmation_code_request(self, session: requests.Session, phone_number: str, confirmation_code: str) -> Tuple[bool, requests.Session]:
        ...
