from abc import ABC, abstractmethod
from typing import Optional

import requests

from src.domain.dtos.fb_katana_enable_two_factor_data import FbKatanaEnableTwoFactorData


class IFbKatanaEnableTwoFactor(ABC):

    @abstractmethod
    def enable(
            self,
            fb_user_id: str,
            fb_password: str,
            fb_access_token: str,
            session: requests.Session
    ) -> tuple[bool, Optional[str], requests.Session]:
        pass

    @property
    @abstractmethod
    def payload(self) -> FbKatanaEnableTwoFactorData:
        pass
