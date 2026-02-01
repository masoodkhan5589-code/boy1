from typing import Optional

from src.application.interfaces.i_fb_app_helper import IFbAppHelper
from src.application.interfaces.i_fb_katana_add_contact_after_sign_up_tut import IFbKatanaAddContactAfterSignUpTut
from src.application.orchestrator.facebook_katana.fb_katana_set_contact_and_get_otp_orchestrator import \
    FbKatanaSetContactAndGetOtpOrchestrator
from src.application.use_cases.facebook_katana.fb_katana_set_contact_and_get_otp_process_use_case import \
    FbKatanaSetContactAndGetOtpProcessUseCase

from src.common.logger import logger
from src.domain.dtos.fb_creator_response_data import FbCreatorResponseData
from src.domain.dtos.fb_katana_verified_payload import FbKatanaVerifiedPayload
from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.setting_loader_data import SettingLoaderData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData
from src.infrastructure.services.facebook.facebook_katana.fb_katana_set_contact_after_sign_up_tut_impl import \
    FbKatanaSetContactAfterSignUpTutImpl

from src.workers.base_request_process import BaseFbRequestProcess


class FbKatanaSetContactAndGetOtpProcess(BaseFbRequestProcess):

    # ------------------ Task Queue ------------------
    def _get_task_item(self, **kwargs) -> Optional[dict]:
        try:
            item = self.accounts_queue.get_nowait()
            raw_fields = [f.strip() for f in str(item).split('|')]

            return {
                "id_source": raw_fields[0],
                "fb_user_id": raw_fields[1],
                "fb_password": raw_fields[2],
                "cookie": raw_fields[4],
                "access_token": raw_fields[5],
            }
        except Exception as _:
            return None

    # ------------------ Helpers ------------------
    @staticmethod
    def _build_handlers(virtual_device_info_data, proxy_payload) -> IFbKatanaAddContactAfterSignUpTut:
        set_contact = FbKatanaSetContactAfterSignUpTutImpl(virtual_device_info_data, proxy_payload)
        return set_contact

    def _build_confirmation_request_orchestrator(
        self,
        verified_payload: FbKatanaVerifiedPayload,
        handler_set_contact: IFbKatanaAddContactAfterSignUpTut,
        fb_request_helper: IFbAppHelper,
        settings: SettingLoaderData
    ) -> FbKatanaSetContactAndGetOtpOrchestrator:
        return FbKatanaSetContactAndGetOtpOrchestrator(
            verified_payload=verified_payload,
            handler_set_contact=handler_set_contact,
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
        fb_user_id = item.get("fb_user_id")
        fb_access_token = item.get("access_token")

        try:

            verified_payload = FbKatanaVerifiedPayload(
                id_source=id_source,
                fb_user_id=fb_user_id,
                fb_access_token=fb_access_token
            )

            handler_set_contact = self._build_handlers(virtual_device_info_data, proxy_payload)

            set_contact_and_get_otp_orchestrator = self._build_confirmation_request_orchestrator(
                settings=settings,
                verified_payload=verified_payload,
                fb_request_helper=fb_request_helper,
                handler_set_contact=handler_set_contact,
            )

            use_case = FbKatanaSetContactAndGetOtpProcessUseCase(
                status_manager=self.status_manager,
                fb_request_helper=fb_request_helper,
                set_contact_and_get_otp_orchestrator=set_contact_and_get_otp_orchestrator,
            )

            return use_case.start()
        except Exception as e:
            logger.error(f"[{id_source}] Error in _run_core_task: {e}", exc_info=True)
            self.update_proxy_status(id_source, status=e)
            return None
