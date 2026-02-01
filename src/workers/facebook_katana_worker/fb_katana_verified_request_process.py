from typing import Optional, Tuple

from src.application.interfaces.i_fb_app_helper import IFbAppHelper
from src.application.interfaces.i_fb_katana_add_contact_after_sign_up_tut import IFbKatanaAddContactAfterSignUpTut
from src.application.interfaces.i_fb_katana_confirmation_tut import IFbKatanaConfirmationTut

from src.application.orchestrator.facebook_katana.fb_katana_verified_request_orchestrator import \
    FbKatanaVerifiedRequestOrchestrator
from src.application.use_cases.facebook_katana.fb_katana_verified_request_use_case import FbKatanaVerifiedRequestUseCase
from src.common.logger import logger
from src.domain.dtos.fb_creator_response_data import FbCreatorResponseData
from src.domain.dtos.fb_katana_verified_payload import FbKatanaVerifiedPayload
from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.setting_loader_data import SettingLoaderData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData
from src.infrastructure.services.facebook.facebook_katana.fb_katana_confirmation_code_tut_impl import \
    FbKatanaConfirmationCodeTutImpl
from src.infrastructure.services.facebook.facebook_katana.fb_katana_set_contact_after_sign_up_tut_impl import \
    FbKatanaSetContactAfterSignUpTutImpl

from src.workers.base_request_process import BaseFbRequestProcess


class FbKatanaVerifiedRequestProcess(BaseFbRequestProcess):

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
    def _build_handlers(virtual_device_info_data, proxy_payload) -> Tuple[
        IFbKatanaAddContactAfterSignUpTut, IFbKatanaConfirmationTut
    ]:
        set_contact = FbKatanaSetContactAfterSignUpTutImpl(virtual_device_info_data, proxy_payload)
        confirmation_code = FbKatanaConfirmationCodeTutImpl(virtual_device_info_data, proxy_payload)
        return set_contact, confirmation_code

    def _build_confirmation_request_orchestrator(
        self,
        verified_payload: FbKatanaVerifiedPayload,
        handler_set_contact: IFbKatanaAddContactAfterSignUpTut,
        handler_confirmation: IFbKatanaConfirmationTut,
        fb_request_helper: IFbAppHelper,
        settings: SettingLoaderData
    ) -> FbKatanaVerifiedRequestOrchestrator:
        return FbKatanaVerifiedRequestOrchestrator(
            verified_payload=verified_payload,
            handler_set_contact=handler_set_contact,
            handler_confirmation=handler_confirmation,
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

            handler_set_contact, handler_confirmation = self._build_handlers(virtual_device_info_data, proxy_payload)

            verified_orchestrator = self._build_confirmation_request_orchestrator(
                settings=settings,
                verified_payload=verified_payload,
                fb_request_helper=fb_request_helper,
                handler_set_contact=handler_set_contact,
                handler_confirmation=handler_confirmation
            )

            use_case = FbKatanaVerifiedRequestUseCase(
                status_manager=self.status_manager,
                fb_request_helper=fb_request_helper,
                verified_orchestrator=verified_orchestrator,
            )

            return use_case.start()
        except Exception as e:
            logger.error(f"[{id_source}] Error in _run_core_task: {e}", exc_info=True)
            self.update_proxy_status(id_source, status=e)
            return None
