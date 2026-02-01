from typing import List, Optional

from PyQt6.QtCore import QThread, pyqtSignal

from src.domain.enums.register_method import RegisterMethod
from src.infrastructure.configuration_service import ConfigurationService
from src.infrastructure.services.generators.virtual_device_info_generator import VirtualDeviceInfoGenerator
from src.common.status_constants import StatusConstants
from src.infrastructure.services.network_services.ip_address_checker import IPAddressChecker
from src.infrastructure.services.proxy_services.proxy_manager import ProxyManager
from src.workers.method_worker_main import MethodWorkerMain


class QProcessWorker(QThread):
    """
    Worker xử lý tác vụ trong một QThread riêng biệt,
    tạo và khởi động WorkerCreatorMain.
    """
    q_process_response_signal = pyqtSignal(object)
    process_stopped_signal = pyqtSignal()

    def __init__(
        self,
        get_is_running: callable,
        set_is_running: callable,
        update_count_bar: callable,
        configuration_service: ConfigurationService,
        selected_items: Optional[List],
        action: str = RegisterMethod.LOGIN_FB_KATANA.value,
    ):
        super().__init__()
        self.get_is_running = get_is_running
        self.set_is_running = set_is_running
        self.update_count_bar = update_count_bar
        self.configuration_service = configuration_service
        self.selected_items = selected_items
        self.action = action

    def run(self):
        """
        Phương thức chính để chạy trong luồng.
        Nó tạo các dependencies và khởi động WorkerCreatorMain.
        """
        # Tạo các dependencies cần thiết cho WorkerCreatorMain
        status_manager_instance = StatusConstants()
        proxies_manager_instance = ProxyManager(release_cooldown=0)
        ip_address_checker = IPAddressChecker()
        virtual_device_info_generator = VirtualDeviceInfoGenerator()

        dependencies = {
            "status_manager": status_manager_instance,
            "proxies_manager": proxies_manager_instance,
            "ip_address_checker": ip_address_checker,
            "virtual_device_info_generator": virtual_device_info_generator,
        }

        # Khởi tạo WorkerCreatorMain với các dependencies đã được tạo
        worker = MethodWorkerMain(
            selected_items=self.selected_items,
            set_is_running=self.set_is_running,
            get_is_running=self.get_is_running,
            update_count_bar=self.update_count_bar,
            q_process_response_signal=self.q_process_response_signal,
            configuration_service=self.configuration_service,
            dependencies=dependencies,
            process_stopped_signal=self.process_stopped_signal,
            action=self.action
        )
        worker.start()
