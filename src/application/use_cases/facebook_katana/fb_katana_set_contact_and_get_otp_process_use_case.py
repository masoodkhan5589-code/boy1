import traceback
from typing import Optional

from src.application.interfaces.i_fb_app_helper import IFbAppHelper
from src.application.orchestrator.facebook_katana.fb_katana_set_contact_and_get_otp_orchestrator import \
    FbKatanaSetContactAndGetOtpOrchestrator
from src.common.logger import logger
from src.common.status_constants import StatusConstants
from src.domain.dtos.fb_creator_response_data import FbCreatorResponseData


class FbKatanaSetContactAndGetOtpProcessUseCase:

    def __init__(
            self,
            status_manager: StatusConstants,
            fb_request_helper: IFbAppHelper,
            set_contact_and_get_otp_orchestrator: FbKatanaSetContactAndGetOtpOrchestrator,
    ) -> None:
        self.fb_request_helper = fb_request_helper
        self.status_manager = status_manager
        self.set_contact_and_get_otp_orchestrator = set_contact_and_get_otp_orchestrator

    def start(self) -> Optional[FbCreatorResponseData]:
        try:
            self._update_result_from_data()

            # Kiểm tra trạng thái tài khoản trước login
            if not self.fb_request_helper.check_live_account():
                return FbCreatorResponseData(**self.fb_request_helper.result)

            # Điều phối logic chính bằng cách gọi các Orchestrator
            if not self.set_contact_and_get_otp_orchestrator.run_flow():
                self.fb_request_helper.error = True

            # Tiếp tục logic sau khi verified hoàn tất
            if (self.fb_request_helper.result.get("uid") and
                    (self.fb_request_helper.result.get("cookie") or self.fb_request_helper.result.get("bearer_token"))):
                self.fb_request_helper.check_live_account(check_info_token=True)

        except Exception as _:
            self.fb_request_helper.error = True
            self.fb_request_helper.update_status(status=self.status_manager.EXCEPTION_ERROR)
            logger.error(f'Execution error in start(): {traceback.format_exc()}')

        return FbCreatorResponseData(**self.fb_request_helper.result)

    def _update_result_from_data(self) -> None:
        self.fb_request_helper.result.update({
            "uid": self.set_contact_and_get_otp_orchestrator.verified_payload.fb_user_id,
            "bearer_token": self.set_contact_and_get_otp_orchestrator.verified_payload.fb_access_token,
        })
