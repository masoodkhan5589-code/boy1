from abc import abstractmethod
from typing import Optional

from src.application.use_cases.detection_manager_use_case import DetectionManagerUseCase
from src.domain.dtos.check_info_token_response_data import CheckInfoTokenResponseData
from src.domain.dtos.fb_katana_login_payload import FbKatanaLoginPayload


class IFbKatanaLogin:

    @abstractmethod
    def __init__(
            self,
            payload: FbKatanaLoginPayload,
            detection_manager: DetectionManagerUseCase,
    ):
        ...

    @abstractmethod
    def open_facebook_app(self) -> bool:
        ...

    @abstractmethod
    def login_account(self, is_restored: bool = False) -> tuple[bool, bool, bool]:
        ...

    @abstractmethod
    def close_facebook_app(self) -> bool:
        ...

    @abstractmethod
    def get_account_data(self, fb_user_id: str, fb_access_token: str) -> CheckInfoTokenResponseData:
        ...

    @abstractmethod
    def fetch_account_information(self) -> tuple[Optional[str], Optional[str], Optional[str], bool]:
        ...

    @abstractmethod
    def _safe_restart_facebook_app(self):
        ...

    @property
    @abstractmethod
    def payload(self) -> FbKatanaLoginPayload:
        ...
