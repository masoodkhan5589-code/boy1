import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from typing import Optional, List, Union

from src.common.execute_tasks import execute_tasks
from src.common.logger import logger
from src.domain.dtos.table_widget_payload_data import TableWidgetPayloadData
from src.domain.entities.counter import Counter
from src.domain.enums.register_method import RegisterMethod
from src.infrastructure.configuration_service import ConfigurationService
from src.workers.facebook_katana_worker.fb_chrome_forgot_password_process import FbChromeForgotPasswordProcess
from src.workers.facebook_katana_worker.fb_katana_login_request_process import FbKatanaLoginProcess
from src.workers.facebook_katana_worker.fb_katana_set_contact_and_get_otp_process import \
    FbKatanaSetContactAndGetOtpProcess
from src.workers.facebook_katana_worker.fb_katana_verified_request_process import FbKatanaVerifiedRequestProcess


class MethodWorkerMain:
    """
    Orchestrator chính để khởi động và quản lý các tiến trình worker.
    """

    def __init__(
            self,
            dependencies: dict,
            set_is_running: callable,
            get_is_running: callable,
            update_count_bar: callable,
            q_process_response_signal: callable,
            selected_items: Optional[List],
            configuration_service: ConfigurationService,
            action: str = RegisterMethod.LOGIN_FB_KATANA.value,
            process_stopped_signal: callable = None
    ):
        self.dependencies = dependencies
        self.set_is_running = set_is_running
        self.get_is_running = get_is_running
        self.update_count_bar = update_count_bar
        self.q_process_response_signal = q_process_response_signal
        self.selected_items = selected_items
        self.configuration_service = configuration_service
        self.action = action

        self.counters = Counter()
        self.lock = threading.Lock()

        self.settings = self.configuration_service.get_settings()

        # Khởi tạo AdbHelper ở đây để dùng chung
        self.process_stopped_signal = process_stopped_signal

    def start(self) -> None:
        """Khởi động tiến trình chính của worker."""
        self.set_is_running(True)

        try:
            worker_class_map = {
                RegisterMethod.LOGIN_FB_KATANA.value: FbKatanaLoginProcess,
                RegisterMethod.VERIFY_FB_KATANA.value: FbKatanaVerifiedRequestProcess,
                RegisterMethod.ADD_CONTACT_KATANA.value: FbKatanaSetContactAndGetOtpProcess,
                RegisterMethod.FORGOT_PASSWORD_KATANA.value: FbChromeForgotPasswordProcess,
            }

            process_class = worker_class_map.get(self.action, FbKatanaLoginProcess)

            # Lấy selected items nếu có
            shared_accounts_queue = Queue()

            if self.action in [
                RegisterMethod.LOGIN_FB_KATANA.value,
                RegisterMethod.VERIFY_FB_KATANA.value,
                RegisterMethod.ADD_CONTACT_KATANA.value,
                RegisterMethod.FORGOT_PASSWORD_KATANA.value,
            ]:
                if len(self.selected_items) < 1:
                    return

                # --- BATCH EMIT CỦA BẠN (Đã sửa) ---
                initial_payloads = []
                for acc in self.selected_items:
                    item_parts = acc.split('|')

                    # 1. Thu thập dữ liệu khởi tạo vào danh sách (Batch)
                    initial_payloads.append(
                        TableWidgetPayloadData(
                            id_source=item_parts[0],
                            account_status=' ',
                            total_time=' ',
                            status=' '
                        )
                    )

                    # 2. Đưa tài khoản vào queue (vẫn là từng mục)
                    shared_accounts_queue.put(acc)

                # 3. Gửi BATCH dữ liệu khởi tạo ra GUI một lần duy nhất
                if initial_payloads:
                    self._response_to_table_widget(data=initial_payloads)

            self._execute_worker_request_process(process_class, shared_accounts_queue)

        except Exception as e:
            import traceback
            logger.error(f"Lỗi khi khởi động worker: {e} - {traceback.format_exc()}")
        finally:
            self.set_is_running(False)
            self.process_stopped_signal.emit()

    # --- Các phương thức main worker dành cho request ---
    def _execute_worker_request_process(self, process_class, shared_accounts_queue):
        """Phương thức chung để thực thi các tiến trình worker."""
        global_threading_lock = threading.Lock()

        max_threads = min(self.settings.global_setting.max_threads, 50)
        device_ids = [str(uuid.uuid4()) for _ in range(max_threads)]

        with ThreadPoolExecutor(max_threads) as executor:
            futures = [executor.submit(
                self._run_request_process_worker, process_class, device_id, global_threading_lock, shared_accounts_queue
            ) for device_id in device_ids[:max_threads]]

            # Chờ tất cả các luồng hoàn thành
            for future in futures:
                future.result()

    def _run_request_process_worker(
            self, process_class, device_id: str, global_threading_lock: threading.Lock, shared_accounts_queue: Queue
    ):
        # Tạo dictionary context
        context_dict = {
            "configuration_service": self.configuration_service,
            "status_manager": self.dependencies["status_manager"],
            "proxies_manager": self.dependencies["proxies_manager"],
            "virtual_device_info_generator": self.dependencies["virtual_device_info_generator"],
            "ip_address_checker": self.dependencies["ip_address_checker"],
            "global_threading_lock": global_threading_lock,
            "execute_tasks": execute_tasks
        }

        # Khởi tạo worker_instance
        worker_instance = process_class(
            context=context_dict,
            accounts_queue=shared_accounts_queue,
            get_account_verified_count=self._get_account_verified_count,
            set_account_verified_count=self._set_account_verified_count,
            get_account_unverified_count=self._get_account_unverified_count,
            set_account_unverified_count=self._set_account_unverified_count,
            get_consecutive_failures=self._get_consecutive_failures,
            set_consecutive_failures=self._set_consecutive_failures,
            check_stop_condition=self._check_stop_condition,
            q_process_response_signal=self.q_process_response_signal,
        )

        while not self._check_stop_condition():
            try:
                worker_instance.execute(device_id)
                break
            except Exception as e:
                import traceback
                logger.error(traceback.format_exc())
                logger.error(f"Lỗi khi xử lý thiết bị {device_id}: {e}")

    # --- Các phương thức đếm và kiểm tra điều kiện ---
    def _get_account_unverified_count(self) -> int:
        with self.lock:
            return self.counters.unverified

    def _set_account_unverified_count(self, unverified_count: int) -> None:
        with self.lock:
            self.counters.unverified = unverified_count

    def _get_account_verified_count(self) -> int:
        with self.lock:
            return self.counters.verified

    def _set_account_verified_count(self, verified_count: int) -> None:
        with self.lock:
            self.counters.verified = verified_count

    def _set_success_count(self, success_count: int) -> None:
        with self.lock:
            self.counters.success = success_count

    def _get_success_count(self) -> int:
        with self.lock:
            return self.counters.success

    def _set_checkpoint_count(self, checkpoint: int) -> None:
        with self.lock:
            self.counters.checkpoint = checkpoint

    def _get_checkpoint_count(self) -> int:
        with self.lock:
            return self.counters.checkpoint

    def _get_consecutive_failures(self) -> int:
        with self.lock:
            return self.counters.consecutive_failures

    def _set_consecutive_failures(self, consecutive_failures: int) -> None:
        with self.lock:
            if consecutive_failures != 0:
                self._update_error_count()
            self.counters.consecutive_failures = consecutive_failures

    def _get_consecutive_disabled(self) -> int:
        with self.lock:
            return self.counters.consecutive_disabled

    def _set_consecutive_disabled(self, consecutive_disabled: int) -> None:
        with self.lock:
            self.counters.consecutive_disabled = consecutive_disabled

    def _response_to_table_widget(self, data: Union[TableWidgetPayloadData, List[TableWidgetPayloadData]]) -> None:
        if self.q_process_response_signal:
            self.q_process_response_signal.emit(data)
        else:
            logger.info(data.status)

    def _update_error_count(self) -> None:
        if self.update_count_bar:
            self.counters.error += 1
            self.update_count_bar(str(self.counters.error))

    def _check_stop_condition(self) -> bool:
        with self.lock:
            return not self.get_is_running()
