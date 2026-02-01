import traceback
from typing import Callable

import requests

from src.application.interfaces.i_fb_app_helper import IFbAppHelper
from src.application.interfaces.i_fb_checker import IFbChecker
from src.application.interfaces.i_fb_katana_add_contact_after_sign_up_tut import IFbKatanaAddContactAfterSignUpTut
from src.application.interfaces.i_fb_katana_confirmation_tut import IFbKatanaConfirmationTut
from src.application.orchestrator.base_request_orchestrator import BaseRequestOrchestrator
from src.common.logger import logger
from src.common.status_constants import StatusConstants
from src.domain.dtos.fb_katana_verified_payload import FbKatanaVerifiedPayload
from src.domain.dtos.setting_loader_data import SettingLoaderData

from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData
from src.domain.enums.opt_service import OtpServices


class FbKatanaVerifiedRequestOrchestrator(BaseRequestOrchestrator):

    def __init__(
            self,
            verified_payload: FbKatanaVerifiedPayload,
            handler_set_contact: IFbKatanaAddContactAfterSignUpTut,
            handler_confirmation: IFbKatanaConfirmationTut,
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

        self.verified_payload = verified_payload
        self.handler_set_contact = handler_set_contact
        self.handler_confirmation = handler_confirmation
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
                (self._set_contact, self.status_manager.ADDING_NEW_CONTACT),
                (self._confirmation_code, self.status_manager.CONFIRMATION_CODE)
            ]

            if not self.execute_tasks(self.fb_request_helper, tasks, max_retries=5):
                return False

            return True

        except Exception as e:
            logger.error(f"Contact verification process failed: {e}\n{traceback.format_exc()}")
            return False

    def _set_contact(self) -> bool:
        if self.fb_request_helper.verified:
            return self.fb_request_helper.update_status(
                is_verified=self.status_manager.VERIFIED,
                status=self.status_manager.ACCOUNT_HAS_BEEN_VERIFIED,
                success=True
            )

        if contact := self._get_contact(virtual_contact=False, secondary_contact=False):
            action_status, self.session = self.handler_set_contact.execute(
                session=self.session,
                fb_access_token=self.verified_payload.fb_access_token,
                contact=contact,
            )

            status = self.status_manager.ADD_CONTACT_SUCCESSFUL \
                if action_status else self.status_manager.ADD_CONTACT_FAILED

            return self.fb_request_helper.update_status(status=status, contact=contact, success=action_status)

        return self.fb_request_helper.update_status(status=self.status_manager.COULD_NOT_GET_NEW_CONTACT, success=False)
    
    def _confirmation_code(self) -> bool:
        if (self.settings.global_setting.otp_service_name == OtpServices.CONTACT_FILE_TXT.value.key
                and '@' not in self.fb_request_helper.primary_otp_service_response.contact):
            return self.fb_request_helper.update_status(
                status=self.status_manager.ADD_CONTACT_SUCCESSFUL,
                success=True
            )

        if self.fb_request_helper.verified:
            return self.fb_request_helper.update_status(
                is_verified=self.status_manager.VERIFIED,
                status=self.status_manager.ACCOUNT_HAS_BEEN_VERIFIED,
                success=True
            )

        if not self.fb_checker.check_uid(self.app_helper.result.get("uid", "")):
            return True

        confirmation_code = self._get_otp_code()
        if not confirmation_code or confirmation_code is None:
            return self.fb_request_helper.update_status(
                status=self.status_manager.COULD_NOT_RETRIEVE_CODE, success=False
            )

        self.fb_request_helper.update_status(
            otp=str(confirmation_code),
            status=self.status_manager.CONFIRMATION_CODE
        )

        action_status, self.session = self.handler_confirmation.execute(
            contact=self.app_helper.primary_otp_service_response.contact,
            confirmation_code=confirmation_code,
            fb_access_token=self.verified_payload.fb_access_token,
            session=self.session
        )

        self.fb_request_helper.verified = action_status
        self.fb_request_helper.unverified = not action_status

        is_verified_status = self.status_manager.VERIFIED if action_status else self.status_manager.UNVERIFIED
        status = self.status_manager.CONFIRMATION_CODE_SUCCESSFUL \
            if action_status else self.status_manager.COULD_NOT_CONFIRM_CODE
        return self.fb_request_helper.update_status(is_verified=is_verified_status, status=status, success=action_status)
