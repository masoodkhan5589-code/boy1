from abc import ABC, abstractmethod
from typing import Tuple

import requests


class IFbKatanaAddContactAfterSignUpTut(ABC):

    @abstractmethod
    def execute(self, contact: str, fb_access_token: str, session: requests.Session) -> Tuple[bool, requests.Session]:
        ...
