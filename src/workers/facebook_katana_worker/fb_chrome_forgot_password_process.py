from typing import Optional

from src.application.interfaces.i_fb_app_helper import IFbAppHelper
from src.application.interfaces.i_fb_chrome_forgot_password_request import IFbChromeForgotPasswordRequest
from src.application.orchestrator.facebook_katana.fb_forgot_password_request_orchestrator import \
    FbForgotPasswordRequestOrchestrator
from src.application.use_cases.facebook_katana.fb_chrome_forgot_password_use_case import FbChromeForgotPasswordUseCase

from src.common.logger import logger
from src.domain.dtos.fb_creator_response_data import FbCreatorResponseData
from src.domain.dtos.fb_forogot_password_payload import FbForgotPasswordPayload
from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.setting_loader_data import SettingLoaderData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData
from src.infrastructure.services.facebook.facebook_katana.fb_chrome_forgot_password_request_impl import \
    FbChromeForgotPasswordRequestImpl

from src.workers.base_request_process import BaseFbRequestProcess


class FbChromeForgotPasswordProcess(BaseFbRequestProcess):

    # ------------------ Task Queue ------------------
    def _get_task_item(self, **kwargs) -> Optional[dict]:
        try:
            item = self.accounts_queue.get_nowait()
            raw_fields = [f.strip() for f in str(item).split('|')]

            return {
                "id_source": raw_fields[0],
                "contact": raw_fields[7],
            }
        except Exception as _:
            return None

    # ------------------ Helpers ------------------
    @staticmethod
    def _build_handlers(virtual_device_info_data, proxy_payload) -> IFbChromeForgotPasswordRequest:
        forgot_password = FbChromeForgotPasswordRequestImpl(virtual_device_info_data, proxy_payload)
        return forgot_password

    def _build_confirmation_request_orchestrator(
        self,
        forgot_password_payload: FbForgotPasswordPayload,
        handler_forgot_password: IFbChromeForgotPasswordRequest,
        fb_request_helper: IFbAppHelper,
        settings: SettingLoaderData
    ) -> FbForgotPasswordRequestOrchestrator:
        return FbForgotPasswordRequestOrchestrator(
            forgot_password_payload=forgot_password_payload,
            handler_forgot_password=handler_forgot_password,
            fb_request_helper=fb_request_helper,
            fb_checker=self.account_checker,
            status_manager=self.status_manager,
            virtual_device_info_data=self.virtual_device_info_data,
            settings=settings,
            execute_tasks=self.execute_tasks,
            check_stop_condition=self.check_stop_condition
        )

    # ------------------ Core Task ------------------
    def _run_core_task(
        self,
        item: dict,
        device_id: str,
        virtual_device_info_data: VirtualDeviceInfoData,
        settings: SettingLoaderData,
        proxy_payload: ProxyPayloadData,
        fb_request_helper: IFbAppHelper,
    ) -> Optional[FbCreatorResponseData]:
        """
        Logic cốt lõi để xác minh một tài khoản Facebook.
        Dependencies có thể inject để test dễ dàng.
        """
        id_source = item.get("id_source")
        contact = item.get("contact")

        try:

            forgot_password_payload = FbForgotPasswordPayload(
                id_source=id_source,
                contact=contact
            )

            handler_forgot_password = self._build_handlers(virtual_device_info_data, proxy_payload)

            forgot_password_orchestrator = self._build_confirmation_request_orchestrator(
                settings=settings,
                forgot_password_payload=forgot_password_payload,
                fb_request_helper=fb_request_helper,
                handler_forgot_password=handler_forgot_password,
            )

            use_case = FbChromeForgotPasswordUseCase(
                status_manager=self.status_manager,
                fb_request_helper=fb_request_helper,
                forgot_password_orchestrator=forgot_password_orchestrator,
            )

            return use_case.start()
        except Exception as e:
            logger.error(f"[{id_source}] Error in _run_core_task: {e}", exc_info=True)
            self.update_proxy_status(id_source, status=e)
            return None
