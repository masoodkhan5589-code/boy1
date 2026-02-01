import time
from datetime import datetime
from typing import Callable, Optional

from src.application.interfaces.i_fb_app_helper import IFbAppHelper
from src.application.interfaces.i_fb_checker import IFbChecker
from src.common.status_constants import StatusConstants
from src.domain.dtos.setting_loader_data import SettingLoaderData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData


class BaseOrchestrator:

    def __init__(
            self,
            settings: SettingLoaderData,
            app_helper: IFbAppHelper,
            status_manager: StatusConstants,
            virtual_device_info_data: VirtualDeviceInfoData,
            account_checker: IFbChecker,
            check_stop_condition: Callable,
    ):
        self.settings = settings
        self.app_helper = app_helper
        self.status_manager = status_manager
        self.virtual_device_info_data = virtual_device_info_data
        self.account_checker = account_checker
        self.check_stop_condition = check_stop_condition

    # ===============================================================
    # MAIN LOGIC
    # ===============================================================
    def _get_contact(self, **kwargs) -> str:
        contact_value: Optional[str] = None

        while not contact_value and not self.check_stop_condition():
            new_contact = self.app_helper.primary_contact_management.get_contact(username=kwargs.get("username"))
            self.app_helper.primary_otp_service_response = new_contact
            contact_value = new_contact.contact if hasattr(new_contact, 'contact') else None

            if not contact_value:
                time.sleep(2)

        return contact_value

    def _get_otp_code(self):
        otp_code = self.app_helper.primary_contact_management.get_otp(
            otp_service_response=self.app_helper.primary_otp_service_response
        )
        return otp_code

    # ===============================================================
    def _update_create_date(self) -> bool:
        create_date = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        return self.app_helper.update_status(create_date=create_date)
