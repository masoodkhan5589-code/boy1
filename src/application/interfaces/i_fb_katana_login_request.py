from abc import ABC, abstractmethod
from typing import Tuple, Optional


class IFbKatanaLoginRequest(ABC):

    @abstractmethod
    def get_auth(self, facebook_username: str, facebook_password: str, two_factor_key: Optional[str]) -> Tuple:
        ...
