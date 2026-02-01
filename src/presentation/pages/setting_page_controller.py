from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QFileDialog

from src.common import config
from src.common.logger import logger
from src.domain.enums.opt_service import OtpServices
from src.domain.enums.proxy_app import ProxyApp
from src.infrastructure.database import Setting
from src.domain.enums.proxy_protocol import ProxyProtocol


class SettingPageController(QObject):
    """
    Class này chỉ xử lý logic lưu trữ và cập nhật các giá trị trong trang cài đặt.
    """

    def __init__(self, ui):
        super().__init__()
        self.ui = ui

        # Khởi tạo các ComboBox
        self._initialize_selections()

        # Load cài đặt từ database
        self._load_settings_from_db()

        # Kết nối các tín hiệu
        self._connect_signals()

    def _connect_signals(self):
        # Nối tất cả các tín hiệu
        self.ui.qspin_max_thread.valueChanged.connect(self._save_setting)

        self.ui.qspin_wait_code_timeout.valueChanged.connect(self._save_setting)
        self.ui.otp_service_select_options.currentIndexChanged.connect(self._save_setting)
        self.ui.otp_service_api_key_input.textChanged.connect(self._save_setting)

        self.ui.radio_button_socks5.toggled.connect(self._save_setting)
        self.ui.radio_button_http.toggled.connect(self._save_setting)
        self.ui.radio_button_https.toggled.connect(self._save_setting)
        self.ui.radio_button_enable_proxy.toggled.connect(self._save_setting)
        self.ui.radio_button_disable_proxy.toggled.connect(self._save_setting)

    def _load_backup_folder(self):
        try:
            # Mở hộp thoại chọn folder
            folder = QFileDialog.getExistingDirectory(
                self.ui.main_window_instance,  # parent widget
                "Chọn thư mục Backup",
                "",
                QFileDialog.Option.ShowDirsOnly
            )

            if not folder:
                return  # Người dùng bấm Cancel

            # Set đường dẫn folder vào ô text
            self.ui.backup_folder_line_view.setText(folder)

        except Exception as e:
            logger.error(f"Unexpected error while selecting backup folder: {e}")

    def _save_setting(self):
        # Lấy giá trị Proxy Protocol
        if self.ui.radio_button_socks5.isChecked():
            proxy_type = ProxyProtocol.SOCKS5.value
        elif self.ui.radio_button_http.isChecked():
            proxy_type = ProxyProtocol.HTTP.value
        else:
            proxy_type = ProxyProtocol.HTTPS.value

        if self.ui.radio_button_enable_proxy.isChecked():
            proxy_enabled = ProxyApp.ENABLE.value.key
        else:
            proxy_enabled = ProxyApp.DISABLED.value.key

        settings = Setting(
            max_threads=int(self.ui.qspin_max_thread.value()),
            wait_code_timeout=int(self.ui.qspin_wait_code_timeout.value()),
            otp_service_name=self.ui.otp_service_select_options.currentData(),
            otp_service_api_key=self.ui.otp_service_api_key_input.text(),
            proxy_type=proxy_type,
            proxy_enabled=proxy_enabled,
        )
        self.ui.gui_controller.save_setting(settings)

    def _load_settings_from_db(self):
        settings_loader_data = self.ui.gui_controller.configuration_service.get_settings()
        if not settings_loader_data or not settings_loader_data.global_setting:
            return

        global_setting = settings_loader_data.global_setting

        # Global Config
        self.ui.qspin_max_thread.setValue(global_setting.max_threads or 1)
        self.ui.radio_button_enable_proxy.setChecked(global_setting.proxy_enabled == ProxyApp.ENABLE.value.key)
        self.ui.radio_button_disable_proxy.setChecked(global_setting.proxy_enabled == ProxyApp.DISABLED.value.key)

        # OTP Service
        self.ui.qspin_wait_code_timeout.setValue(int(global_setting.wait_code_timeout or 90))
        self._set_combobox_from_value(self.ui.otp_service_select_options, global_setting.otp_service_name)
        self.ui.otp_service_api_key_input.setText(global_setting.otp_service_api_key or "")

        # Proxy
        if global_setting.proxy_type == ProxyProtocol.HTTP.value:
            self.ui.radio_button_http.setChecked(True)
        elif global_setting.proxy_type == ProxyProtocol.HTTPS.value:
            self.ui.radio_button_https.setChecked(True)
        else:
            self.ui.radio_button_socks5.setChecked(True)

        if global_setting.proxy_enabled == ProxyApp.ENABLE.value.key:
            self.ui.radio_button_enable_proxy.setChecked(True)
        else:
            self.ui.radio_button_disable_proxy.setChecked(True)

    def _initialize_selections(self):
        # Tải các tùy chọn cho các ComboBox
        self._populate_combobox(self.ui.otp_service_select_options, OtpServices, exclude_dev_mode=True)

    @staticmethod
    def _populate_combobox(combobox, enum_class, exclude_dev_mode=False):
        """
        Điền dữ liệu vào QComboBox từ Enum, tự động group theo logic:
        - Nếu có DISABLED → group riêng.
        - Với OtpServices → chia Email vs Phone.
        - Các enum khác → group Disabled vs Options.
        """
        combobox.clear()

        # Xử lý riêng cho OtpServices
        if enum_class.__name__ == "OtpServices":
            groups = {
                "Email Services": [e for e in enum_class if "mail" in e.value.key],
                "Phone Services": [e for e in enum_class if "phone" in e.value.key],
            }
        else:
            # Các enum khác: tách Disabled vs Others
            disabled = [e for e in enum_class if "disable" in e.value.key or "disabled" in e.value.key]
            others = [e for e in enum_class if e not in disabled]
            groups = {}
            if disabled:
                groups["Disabled"] = disabled
            if others:
                groups["Options"] = others

        for group_name, items in groups.items():
            # Add group label
            combobox.addItem(f"--- {group_name} ---", None)
            idx = combobox.count() - 1
            combobox.model().item(idx).setEnabled(False)

            for data in items:
                key = data.value.label
                value = data.value.key
                if exclude_dev_mode and not config.development_mode and value in ['email_custom_domain']:
                    continue
                combobox.addItem(key, value)

            # separator
            combobox.insertSeparator(combobox.count())

        # Xóa separator cuối cùng nếu có
        last_index = combobox.count() - 1
        if combobox.itemText(last_index) == "":
            combobox.removeItem(last_index)

    @staticmethod
    def _set_combobox_from_value(combobox, value):
        """Chọn item theo data (key), bỏ qua group label (data=None)."""
        if value is None:
            return
        for i in range(combobox.count()):
            if combobox.itemData(i) == value:
                combobox.setCurrentIndex(i)
                break
