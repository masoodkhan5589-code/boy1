import traceback
from typing import Optional

from src.application.interfaces.i_fb_app_helper import IFbAppHelper
from src.application.orchestrator.facebook_katana.fb_forgot_password_request_orchestrator import \
    FbForgotPasswordRequestOrchestrator
from src.common.logger import logger
from src.common.status_constants import StatusConstants
from src.domain.dtos.fb_creator_response_data import FbCreatorResponseData


class FbChromeForgotPasswordUseCase:

    def __init__(
            self,
            status_manager: StatusConstants,
            fb_request_helper: IFbAppHelper,
            forgot_password_orchestrator: FbForgotPasswordRequestOrchestrator,
    ) -> None:
        self.fb_request_helper = fb_request_helper
        self.status_manager = status_manager
        self.forgot_password_orchestrator = forgot_password_orchestrator

    def start(self) -> Optional[FbCreatorResponseData]:
        try:
            self._update_result_from_data()

            # Điều phối logic chính bằng cách gọi các Orchestrator
            if not self.forgot_password_orchestrator.run_flow():
                self.fb_request_helper.error = True

            if not self.fb_request_helper.error and not self.fb_request_helper.account_disabled:
                self.fb_request_helper.update_status(status=self.status_manager.RECOVERY_SUCCESSFUL)
        except Exception as _:
            self.fb_request_helper.error = True
            self.fb_request_helper.update_status(status=self.status_manager.EXCEPTION_ERROR)
            logger.error(f'Execution error in start(): {traceback.format_exc()}')

        return FbCreatorResponseData(**self.fb_request_helper.result)

    def _update_result_from_data(self) -> None:
        self.fb_request_helper.result.update({
            "contact": self.forgot_password_orchestrator.forgot_password_payload.contact
        })
