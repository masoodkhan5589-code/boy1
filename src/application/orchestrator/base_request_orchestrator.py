from typing import Callable

from src.application.interfaces.i_fb_app_helper import IFbAppHelper
from src.application.interfaces.i_fb_checker import IFbChecker
from src.application.orchestrator.base_orchestrator import BaseOrchestrator
from src.common.status_constants import StatusConstants
from src.domain.dtos.setting_loader_data import SettingLoaderData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData


class BaseRequestOrchestrator(BaseOrchestrator):
    def __init__(
            self,
            settings: SettingLoaderData,
            app_helper: IFbAppHelper,
            status_manager: StatusConstants,
            virtual_device_info_data: VirtualDeviceInfoData,
            account_checker: IFbChecker,
            check_stop_condition: Callable,
    ):
        super().__init__(
            settings=settings,
            app_helper=app_helper,
            status_manager=status_manager,
            virtual_device_info_data=virtual_device_info_data,
            account_checker=account_checker,
            check_stop_condition=check_stop_condition,
        )
