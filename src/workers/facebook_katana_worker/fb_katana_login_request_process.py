from typing import Optional

from src.application.interfaces.i_fb_app_helper import IFbAppHelper
from src.application.interfaces.i_fb_katana_login_request import IFbKatanaLoginRequest

from src.application.orchestrator.facebook_katana.fb_katana_login_request_orchestrator import \
    FbKatanaLoginRequestOrchestrator
from src.application.use_cases.facebook_katana.fb_katana_login_request_use_case import FbKatanaLoginRequestUseCase
from src.common.logger import logger
from src.domain.dtos.fb_creator_response_data import FbCreatorResponseData
from src.domain.dtos.fb_katana_login_payload import FbKatanaLoginPayload
from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.setting_loader_data import SettingLoaderData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData
from src.infrastructure.services.facebook.facebook_katana.fb_katana_login_request_impl import FbKatanaLoginRequestImpl

from src.workers.base_request_process import BaseFbRequestProcess


class FbKatanaLoginProcess(BaseFbRequestProcess):

    app_type = "facebook"

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
    def _build_handlers(virtual_device_info_data, proxy_payload) -> IFbKatanaLoginRequest:
        sign_in = FbKatanaLoginRequestImpl(virtual_device_info_data, proxy_payload)
        return sign_in

    def _build_login_orchestrator(
        self,
        login_payload: FbKatanaLoginPayload,
        handler_sign_in: IFbKatanaLoginRequest,
        fb_request_helper: IFbAppHelper,
        settings: SettingLoaderData
    ) -> FbKatanaLoginRequestOrchestrator:
        return FbKatanaLoginRequestOrchestrator(
            login_payload=login_payload,
            handler_sign_in=handler_sign_in,
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
        fb_password = item.get("fb_password")
        fb_two_factor = item.get("twofactor")

        try:

            login_payload = FbKatanaLoginPayload(
                id_source=id_source,
                fb_user_id=fb_user_id,
                fb_password=fb_password,
                fb_two_factor=fb_two_factor
            )

            handler_sign_in = self._build_handlers(virtual_device_info_data, proxy_payload)

            login_orchestrator = self._build_login_orchestrator(
                settings=settings,
                login_payload=login_payload,
                fb_request_helper=fb_request_helper,
                handler_sign_in=handler_sign_in,
            )

            use_case = FbKatanaLoginRequestUseCase(
                status_manager=self.status_manager,
                fb_request_helper=fb_request_helper,
                login_orchestrator=login_orchestrator,
            )

            return use_case.start()
        except Exception as e:
            logger.error(f"[{id_source}] Error in _run_core_task: {e}", exc_info=True)
            self.update_proxy_status(id_source, status=e)
            return None
