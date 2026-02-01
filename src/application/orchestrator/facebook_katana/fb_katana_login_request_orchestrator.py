import traceback
from typing import Callable

import requests

from src.application.interfaces.i_fb_checker import IFbChecker
from src.application.interfaces.i_fb_app_helper import IFbAppHelper
from src.application.interfaces.i_fb_katana_login_request import IFbKatanaLoginRequest
from src.application.orchestrator.base_request_orchestrator import BaseRequestOrchestrator
from src.common.logger import logger
from src.common.status_constants import StatusConstants
from src.domain.dtos.fb_katana_login_payload import FbKatanaLoginPayload
from src.domain.dtos.setting_loader_data import SettingLoaderData

from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData


class FbKatanaLoginRequestOrchestrator(BaseRequestOrchestrator):

    def __init__(
            self,
            login_payload: FbKatanaLoginPayload,
            handler_sign_in: IFbKatanaLoginRequest,
            fb_request_helper: IFbAppHelper,
            fb_checker: IFbChecker,
            status_manager: StatusConstants,
            virtual_device_info_data: VirtualDeviceInfoData,
            check_stop_condition: Callable,
            settings: SettingLoaderData,
            execute_tasks: Callable
    ) -> None:
        super().__init__(
            settings=settings,
            status_manager=status_manager,
            virtual_device_info_data=virtual_device_info_data,
            app_helper=fb_request_helper,
            account_checker=fb_checker,
            check_stop_condition=check_stop_condition,
        )

        self.login_payload = login_payload
        self.handler_sign_in = handler_sign_in
        self.fb_request_helper = fb_request_helper
        self.fb_checker = fb_checker
        self.status_manager = status_manager
        self.virtual_device_info_data = virtual_device_info_data
        self.execute_tasks = execute_tasks

        self.settings = settings
        self.session = requests.Session()

    def run_flow(self) -> bool:
        try:
            login_tasks = [
                (self._sign_in, self.status_manager.STARTING_LOGIN)
            ]

            if not self.execute_tasks(self.fb_request_helper, login_tasks, max_retries=5):
                return False

            return True

        except Exception as e:
            logger.error(f"Contact verification process failed: {e}\n{traceback.format_exc()}")
            return False

    def _sign_in(self) -> bool:
        c_user, cookie, access_token = self.handler_sign_in.get_auth(
            facebook_username=self.login_payload.fb_user_id,
            facebook_password=self.login_payload.fb_password,
            two_factor_key=self.login_payload.fb_two_factor
        )

        is_success = bool(c_user) and bool(access_token) and bool(cookie)
        status = self.status_manager.LOGIN_SUCCESS if is_success else self.status_manager.LOGIN_FAILED

        return self.fb_request_helper.update_status(
            cookie=cookie,
            bearer_token=access_token,
            status=status,
            success=is_success,
        )
