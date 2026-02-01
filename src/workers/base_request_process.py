import time
from abc import ABC, abstractmethod
from queue import Queue
from typing import Optional, Dict, Any, Tuple

from src.application.interfaces.i_device_info_generator import IDeviceInfoGenerator
from src.common.logger import logger
from src.domain.enums.proxy_app import ProxyApp
from src.infrastructure.clients.fb_checker import FbChecker
from src.infrastructure.helpers.fb_request_helper import FbRequestHelper
from src.workers.base_process import BaseProcess
from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.setting_loader_data import SettingLoaderData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData
from src.domain.dtos.fb_creator_response_data import FbCreatorResponseData


class BaseFbRequestProcess(BaseProcess, ABC):

    app_type = "facebook"

    def __init__(
            self,
            context: Dict[str, Any],
            accounts_queue: Queue,
            get_account_verified_count: callable,
            set_account_verified_count: callable,
            get_account_unverified_count: callable,
            set_account_unverified_count: callable,
            get_consecutive_failures: callable,
            set_consecutive_failures: callable,
            check_stop_condition: callable,
            q_process_response_signal: callable
    ):
        super().__init__(q_process_response_signal)

        self.accounts_queue = accounts_queue
        self.get_account_verified_count = get_account_verified_count
        self.set_account_verified_count = set_account_verified_count
        self.get_account_unverified_count = get_account_unverified_count
        self.set_account_unverified_count = set_account_unverified_count
        self.get_consecutive_failures = get_consecutive_failures
        self.set_consecutive_failures = set_consecutive_failures
        self.check_stop_condition = check_stop_condition
        self.context = context

        self.status_manager = context["status_manager"]
        self.proxies_manager = context["proxies_manager"]
        self.execute_tasks = context["execute_tasks"]
        self.virtual_device_info_generator: IDeviceInfoGenerator = context["virtual_device_info_generator"]

        self.account_checker = FbChecker()

        self.virtual_device_info_data: Optional[VirtualDeviceInfoData] = None

    def execute(
            self,
            device_id: str,
            **kwargs
    ) -> None:
        """
        Phương thức chính chứa luồng xử lý chung cho mọi tác vụ (tạo hoặc xác minh).
        """
        item = self._get_task_item()

        proxy_data = ProxyPayloadData()
        virtual_device_info_data = None
        keep_proxy = False

        try:
            while not self.check_stop_condition():

                if not item:
                    break

                start_time = time.time()
                id_source = item.get("id_source")
                settings: SettingLoaderData = self.context["configuration_service"].get_settings()
                request_helper = self._build_fb_request_helper(id_source, settings)

                # -------- Get proxy --------#
                if settings.global_setting.proxy_enabled == ProxyApp.ENABLE.value.key:
                    proxy_data = self._handle_get_proxy(proxy_data.proxy_uid, settings, keep_proxy)

                #-------- Check IP --------#
                self.update_proxy_status(
                    id_source,
                    device=device_id,
                    proxy=proxy_data.proxy,
                    status=self.status_manager.CHECKING_IP_ADDRESS
                )
                ip_address, country_code = self._check_ip_address(proxy_data.proxy)
                proxy_data.country_code = country_code

                if ip_address is None:
                    keep_proxy = False

                    self.update_proxy_status(
                        id_source, proxy=proxy_data.proxy, status=self.status_manager.COULD_NOT_GET_IP_ADDRESS
                    )
                    time.sleep(10)
                    continue

                self.update_proxy_status(id_source, ip_address=ip_address)

                #-------- Change virtual device --------#
                if not virtual_device_info_data:
                    self.update_proxy_status(
                        id_source,
                        device=device_id,
                        status=self.status_manager.PREPARING_VIRTUAL_DEVICE_INFO
                    )
                    virtual_device_info_data = self.virtual_device_info_generator.generate(
                        country_code=country_code
                    )
                    self.virtual_device_info_data = virtual_device_info_data

                #-------- Thực thi tiến trình --------#
                response_data = self._run_core_task(
                    item,
                    device_id,
                    virtual_device_info_data,
                    settings,
                    proxy_data,
                    request_helper
                )

                if not response_data:
                    keep_proxy = False
                    continue

                # -------- Cập nhật bộ đếm --------#
                self._update_counters(response_data)

                # -------- Lấy trạng thái của tiến trình --------#
                is_success = self._is_account_success(response_data)

                # Log điểm proxy theo country
                self.proxies_manager.report_result(proxy_data.proxy_uid, country_code, is_success)

                # Xử lý các tác vụ khác
                if not is_success:
                    virtual_device_info_data = None

                request_helper.primary_otp_service_response = None
                request_helper.secondary_otp_service_response = None

                # Xử lý tạo hàng mới trên bảng
                if response_data.account_status in [
                    self.status_manager.ACCOUNT_DISABLED,
                    self.status_manager.ACCOUNT_LIVE
                ] or response_data.status in [
                    self.status_manager.RECOVERY_SUCCESSFUL,
                    self.status_manager.RECOVERY_FAILED,
                ]:
                    item = self._get_task_item()

                # Tính tổng time hoàn tất tiến trình
                end_time = time.time()
                elapsed_time = end_time - start_time
                self.update_proxy_status(id_source, total_time=f"{elapsed_time:.2f}s")

        except Exception as e:
            import traceback
            logger.error(traceback.format_exc())
            logger.error(f"Lỗi trong quá trình thực thi cho thiết bị {device_id}: {e}")
            self.set_consecutive_failures(self.get_consecutive_failures() + 1)
        finally:
            if proxy_data:
                self.proxies_manager.release_proxy(proxy_data.proxy_uid)

    @abstractmethod
    def _run_core_task(
            self,
            item: dict,
            device_id: str,
            virtual_device_info_data: VirtualDeviceInfoData,
            settings: SettingLoaderData,
            proxy_payload: ProxyPayloadData,
            request_helper: FbRequestHelper
    ) -> Optional[FbCreatorResponseData]:
        """Phương thức trừu tượng để chạy tác vụ chính (tạo hoặc xác minh)."""
        pass

    @abstractmethod
    def _get_task_item(self, **kwargs) -> Optional[dict]:
        """Phương thức trừu tượng để lấy một item để xử lý (tạo mới hoặc lấy từ DB)."""
        pass

    def _handle_get_proxy(
            self,
            proxy_uid: Optional[str],
            settings: SettingLoaderData,
            keep_proxy: bool = False
    ) -> ProxyPayloadData:

        if proxy_uid:
            self.proxies_manager.release_proxy(proxy_uid)

        proxy_uid, proxy_str = self.proxies_manager.get_proxy(
            uid=proxy_uid if keep_proxy else None
        ) or (None, None)
        if not proxy_uid:
            return ProxyPayloadData()

        return ProxyPayloadData(
            proxy_uid=proxy_uid,
            proxy=f"{settings.global_setting.proxy_type.lower()}://{proxy_str}",
            proxy_protocol=settings.global_setting.proxy_type
        )

    def _check_ip_address(
            self,
            proxy: str
    ) -> Tuple[Optional[str], Optional[str]]:
        ip_address = self.context["ip_address_checker"].get_current_ip(proxy)
        country_code = self.context["ip_address_checker"].get_current_country_code()

        return ip_address, country_code

    def _update_counters(self, response_data: FbCreatorResponseData) -> None:
        if response_data.status not in [self.status_manager.COULD_NOT_GET_NEW_CONTACT]:
            if response_data.account_status not in [self.status_manager.ACCOUNT_LIVE]:
                self.set_consecutive_failures(self.get_consecutive_failures() + 1)
            else:
                self.set_consecutive_failures(0)

        if str(response_data.is_verified).lower() == self.status_manager.VERIFIED:
            self.set_account_verified_count(self.get_account_verified_count() + 1)
        elif str(response_data.is_verified).lower() == self.status_manager.UNVERIFIED:
            self.set_account_unverified_count(self.get_account_unverified_count() + 1)

    def _build_fb_request_helper(self, id_source: str, settings: SettingLoaderData) -> FbRequestHelper:
        return FbRequestHelper(
            response_to_table_widget=self.response_to_table_widget,
            proxies_manager=self.proxies_manager,
            status_manager=self.status_manager,
            id_source=id_source,
            settings=settings,
            execute_tasks=self.execute_tasks
        )

    def _is_account_success(self, response_data) -> bool:
        if response_data.account_status != self.status_manager.ACCOUNT_LIVE:
            return False
        if self.app_type == "facebook":
            return response_data.is_verified in (
                self.status_manager.VERIFIED,
                self.status_manager.UNVERIFIED,
            )
        return True
