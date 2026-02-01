from abc import ABC, abstractmethod
from typing import Optional, Union

import requests


class IMakeRequest(ABC):

    @abstractmethod
    def make_post_request(
        self,
        end_point: str,
        headers: Optional[dict] = None,
        session: Optional[requests.Session] = None,
        body: Optional[Union[str, dict, bytes]] = None,
        files: Optional[dict] = None,
        proxy: Optional[str] = None,
        verify_ssl: bool = True,
        timeout: int = 30
    ) -> any:
        pass

    @abstractmethod
    def make_get_request(
        self,
        end_point: str,
        headers: Optional[dict] = None,
        proxy: Optional[str] = None,
        verify_ssl: bool = True,
        session: Optional[requests.Session] = None,
        timeout: int = 30
    ) -> any:
        pass
