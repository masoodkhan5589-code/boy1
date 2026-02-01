from abc import ABC, abstractmethod
from typing import Tuple

import requests

from src.domain.dtos.fb_katana_add_secondary_contact_data import FbKatanaAddSecondaryContactData


class IFbKatanaAddContactRequest(ABC):

    @abstractmethod
    def add_contact(
            self,
            new_contact: str,
            fb_user_id: str,
            fb_access_token: str,
            session: requests.Session
    ) -> tuple[bool, bool, requests.Session]:
        pass

    @abstractmethod
    def send_confirmation_code_to_previous_contact(
            self,
            primary_contact: str,
            fb_access_token: str,
            session: requests.Session
    ) -> Tuple[bool, requests.Session]:
        pass

    @abstractmethod
    def two_step_verification_verify_code_async(
            self,
            primary_contact: str,
            confirmation_code: str | int,
            fb_access_token: str,
            fb_user_id: str,
            session: requests.Session
    ) -> Tuple[bool, requests.Session]:
        pass

    @abstractmethod
    def confirmation(
            self,
            new_contact: str,
            confirmation_code: str | int,
            fb_user_id: str,
            fb_access_token: str,
            session: requests.Session
    ) -> Tuple[bool, requests.Session]:
        pass

    @property
    @abstractmethod
    def payload(self) -> FbKatanaAddSecondaryContactData:
        pass
