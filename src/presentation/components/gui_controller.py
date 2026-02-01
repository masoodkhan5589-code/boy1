import webbrowser
from typing import Optional, List

from src.domain.enums.register_method import RegisterMethod
from src.infrastructure.configuration_service import ConfigurationService
from src.infrastructure.database import Setting
from src.presentation.components import (
    QProcesCheckInfoToken,
    QProcessCheckLiveAccount, QProcessWorker,
)


class GUIController:

    def __init__(self):
        self.process = None

        # instance duy nhất của service quản lý cấu hình
        self.configuration_service = ConfigurationService()

        self.connection_devices = set()

        # Từ điển để lưu trữ các hàm callback
        self._process_callbacks = {}

    def _cleanup_process_callback(self, process):
        """Xóa callback khỏi từ điển khi tiến trình hoàn thành."""
        self._process_callbacks.pop(process, None)

    @staticmethod
    def handle_contact_support():
        webbrowser.open('https://t.me/endpointsynergy')

    def handle_login(
        self,
        add_or_update_row: callable,
        get_is_running: callable,
        set_is_running: callable,
        update_count_bar: callable,
        selected_items: Optional[List]
    ):
        self.process = QProcessWorker(
            get_is_running=get_is_running,
            set_is_running=set_is_running,
            update_count_bar=update_count_bar,
            configuration_service=self.configuration_service,
            selected_items=selected_items,
            action=RegisterMethod.LOGIN_FB_KATANA.value
        )

        self._process_callbacks[self.process] = add_or_update_row
        self.process.q_process_response_signal.connect(
            lambda data, p=self.process: self.q_process_response_signal(p, data)
        )
        self.process.finished.connect(lambda: self._cleanup_process_callback(self.process))
        self.process.start()

    def handle_verify_account_api_android(
        self,
        add_or_update_row: callable,
        get_is_running: callable,
        set_is_running: callable,
        update_count_bar: callable,
        selected_items: Optional[List]
    ):
        self.process = QProcessWorker(
            get_is_running=get_is_running,
            set_is_running=set_is_running,
            update_count_bar=update_count_bar,
            configuration_service=self.configuration_service,
            selected_items=selected_items,
            action=RegisterMethod.VERIFY_FB_KATANA.value
        )

        self._process_callbacks[self.process] = add_or_update_row
        self.process.q_process_response_signal.connect(
            lambda data, p=self.process: self.q_process_response_signal(p, data)
        )
        self.process.finished.connect(lambda: self._cleanup_process_callback(self.process))
        self.process.start()

    def handle_verify_without_submit_code_api_android_action(
        self,
        add_or_update_row: callable,
        get_is_running: callable,
        set_is_running: callable,
        update_count_bar: callable,
        selected_items: Optional[List]
    ):
        self.process = QProcessWorker(
            get_is_running=get_is_running,
            set_is_running=set_is_running,
            update_count_bar=update_count_bar,
            configuration_service=self.configuration_service,
            selected_items=selected_items,
            action=RegisterMethod.ADD_CONTACT_KATANA.value
        )

        self._process_callbacks[self.process] = add_or_update_row
        self.process.q_process_response_signal.connect(
            lambda data, p=self.process: self.q_process_response_signal(p, data)
        )
        self.process.finished.connect(lambda: self._cleanup_process_callback(self.process))
        self.process.start()

    def handle_forgot_password_action(
        self,
        add_or_update_row: callable,
        get_is_running: callable,
        set_is_running: callable,
        update_count_bar: callable,
        selected_items: Optional[List]
    ):
        self.process = QProcessWorker(
            get_is_running=get_is_running,
            set_is_running=set_is_running,
            update_count_bar=update_count_bar,
            configuration_service=self.configuration_service,
            selected_items=selected_items,
            action=RegisterMethod.FORGOT_PASSWORD_KATANA.value
        )

        self._process_callbacks[self.process] = add_or_update_row
        self.process.q_process_response_signal.connect(
            lambda data, p=self.process: self.q_process_response_signal(p, data)
        )
        self.process.finished.connect(lambda: self._cleanup_process_callback(self.process))
        self.process.start()

    def handle_check_live_facebook_account(
            self,
            add_or_update_row: callable,
            select_rows: list
    ):
        self.process = QProcessCheckLiveAccount(select_rows=select_rows)

        self._process_callbacks[self.process] = add_or_update_row
        self.process.q_process_response_signal.connect(
            lambda data, p=self.process: self.q_process_response_signal(p, data)
        )
        self.process.finished.connect(lambda: self._cleanup_process_callback(self.process))
        self.process.start()

    def handle_check_info_token(
            self,
            add_or_update_row: callable,
            select_rows: list
    ):
        self.process = QProcesCheckInfoToken(select_rows=select_rows)

        self._process_callbacks[self.process] = add_or_update_row
        self.process.q_process_response_signal.connect(
            lambda data, p=self.process: self.q_process_response_signal(p, data)
        )
        self.process.finished.connect(lambda: self._cleanup_process_callback(self.process))
        self.process.start()

    # ================== Others ================== #
    def save_setting(self, setting: Setting):
        # Sử dụng service để lưu cài đặt
        self.configuration_service.save_settings_to_db(setting)

    def q_process_response_signal(self, process, data) -> None:
        """
        Xử lý tín hiệu phản hồi từ worker.
        Dữ liệu có thể là 1 đối tượng đơn lẻ hoặc 1 list đối tượng (cho batch emit).
        """
        if process in self._process_callbacks:
            callback = self._process_callbacks[process]
            if callback:
                if isinstance(data, list):
                    # Nếu là danh sách (batch emit):
                    # Chuyển đổi mỗi đối tượng trong list thành dict
                    list_of_dicts = [vars(item) for item in data]
                    callback(list_of_dicts)
                else:
                    # Nếu là đối tượng đơn lẻ (single emit):
                    # Chuyển đổi đối tượng thành dict (như cũ)
                    callback(vars(data))
