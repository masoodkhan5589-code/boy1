from abc import ABC, abstractmethod
from typing import Tuple

import requests

from src.domain.dtos.fb_katana_remove_contact_data import FbKatanaRemoveContactData


class IFbKatanaRemovePrimaryContactRequest(ABC):

    @abstractmethod
    def remove(self, fb_user_id: str, fb_access_token: str, session: requests.Session) -> Tuple[bool, requests.Session]:
        pass

    @property
    @abstractmethod
    def payload(self) -> FbKatanaRemoveContactData:
        pass
