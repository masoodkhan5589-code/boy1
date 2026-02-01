from abc import ABC, abstractmethod
from typing import Tuple

import requests


class IFbKatanaConfirmationTut(ABC):

    @abstractmethod
    def execute(self, contact: str, confirmation_code: str | int, session: requests.Session, fb_access_token: str) -> Tuple[bool, requests.Session]:
        ...
