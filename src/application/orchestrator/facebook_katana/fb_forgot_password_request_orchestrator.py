import time
import traceback
from typing import Callable

import requests

from src.application.interfaces.i_fb_app_helper import IFbAppHelper
from src.application.interfaces.i_fb_checker import IFbChecker
from src.application.interfaces.i_fb_chrome_forgot_password_request import IFbChromeForgotPasswordRequest
from src.application.orchestrator.base_request_orchestrator import BaseRequestOrchestrator
from src.common.status_constants import StatusConstants
from src.domain.dtos.fb_forogot_password_payload import FbForgotPasswordPayload
from src.domain.dtos.otp_service_response import OTPServiceResponse
from src.domain.dtos.setting_loader_data import SettingLoaderData

from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData


class FbForgotPasswordRequestOrchestrator(BaseRequestOrchestrator):

    def __init__(
            self,
            forgot_password_payload: FbForgotPasswordPayload,
            handler_forgot_password: IFbChromeForgotPasswordRequest,
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

        self.forgot_password_payload = forgot_password_payload
        self.handler_forgot_password = handler_forgot_password
        self.fb_request_helper = fb_request_helper
        self.fb_checker = fb_checker
        self.status_manager = status_manager
        self.virtual_device_info_data = virtual_device_info_data
        self.execute_tasks = execute_tasks

        self.settings = settings
        self.session = requests.Session()

    def run_flow(self) -> bool:
        try:
            tasks = [
                (self._get_facebook_page, self.status_manager.GETTING_FACEBOOK_PAGE),
                (self._recover, self.status_manager.START_RECOVER_ACCOUNT),
                (self._get_redirect_page, self.status_manager.PAGE_REDIRECTING),
                (self._send_recovery_request, self.status_manager.START_RECOVER_ACCOUNT),
                (self._confirmation_code, self.status_manager.CONFIRMATION_CODE)
            ]

            if not self.execute_tasks(self.fb_request_helper, tasks, max_retries=5):
                return False

            return self.app_helper.update_status(
                status=self.status_manager.RECOVERY_SUCCESSFUL,
                success=True
            )

        except Exception as e:
            return self.app_helper.update_status(
                status=f"Contact verification process failed: {e}\n{traceback.format_exc()}",
                success=False
            )

    def _get_facebook_page(self) -> bool:
        action_status, self.session = self.handler_forgot_password.get_facebook_page(session=self.session)
        return action_status

    def _recover(self) -> bool:
        action_status, self.session = self.handler_forgot_password.recover(
            contact=self.forgot_password_payload.contact,
            session=self.session
        )
        return action_status

    def _get_redirect_page(self):
        action_status, self.session = self.handler_forgot_password.get_redirect_page(session=self.session)
        return action_status

    def _send_recovery_request(self):
        success = False
        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            self.fb_request_helper.update_status(
                status=f"Attempt {attempt}/{max_attempts}: Sending password recovery request..."
            )

            action_status, response_message, self.session = self.handler_forgot_password.send_recovery_request(session=self.session)

            if action_status:
                success = True

            self.fb_request_helper.update_status(status=response_message)
            time.sleep(5)

        if not success:
            self.fb_request_helper.update_status(status=f"All recovery attempts failed.")

        return success

    def _confirmation_code(self):
        self.app_helper.primary_otp_service_response = OTPServiceResponse(
            contact=self.forgot_password_payload.contact,
            additional_value=self.forgot_password_payload.contact
        )
        confirmation_code = self._get_otp_code()

        if not confirmation_code:
            return self.app_helper.update_status(
                status=self.status_manager.COULD_NOT_RETRIEVE_CODE,
                success=False
            )

        action_status, self.session = self.handler_forgot_password.confirmation_code_request(
            phone_number=self.forgot_password_payload.contact,
            confirmation_code=confirmation_code,
            session=self.session
        )
        return action_status
