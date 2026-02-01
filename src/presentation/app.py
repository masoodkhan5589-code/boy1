import psutil
from PyQt6.QtWidgets import QMenu, QGraphicsOpacityEffect
from PyQt6.uic.properties import QtCore

from src.presentation.components.qt_dialog import QtDialog
from src.presentation.ui.resources import *
from PyQt6.QtCore import QObject, QTimer, QPropertyAnimation, QEasingCurve

from src.presentation.pages.facebook_page_controller import FacebookPageController
from src.presentation.pages.setting_page_controller import SettingPageController
from src.presentation.components.gui_controller import GUIController
from src.presentation.ui.device_management import Ui_MetaAcctXpert


class App(QObject, Ui_MetaAcctXpert):

    def __init__(self):
        super().__init__()
        self.main_window_instance = None

        self.gui_controller = GUIController()

        # Khởi tạo controller
        self.facebook_controller = None
        self.instagram_controller = None
        self.setting_controller = None
        self.device_controller = None
        self.connection_device = []

        # Ram | CPU
        psutil.cpu_percent(interval=None)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_sys_info)
        self.timer.start(1500)

    def retranslateUi(self, MetaAcctXpert):
        _translate = QtCore.QCoreApplication.translate
        MetaAcctXpert.setWindowTitle(_translate("MetaAcctXpert", "Masood Meta Tool"))
        self.label_version.setText(_translate("MetaAcctXpert", "Version"))
        self.version.setText(_translate("MetaAcctXpert", "1.0.0.4"))
        self.toolButton_facebook.setText(_translate("MetaAcctXpert", "Facebook"))
        self.toolButton_settings.setText(_translate("MetaAcctXpert", "Settings"))
        self.fb_creator_label.setText(_translate("MetaAcctXpert", "Facebook"))
        self.cpu_ram_label_fb_creator.setText(_translate("MetaAcctXpert", "CPU: 3.2% | RAM: 12.5%"))
        self.label_all_fb_creator.setText(_translate("MetaAcctXpert", "Total:"))
        self.label_count_all_fb_creator.setText(_translate("MetaAcctXpert", "0"))
        self.label_selected_fb_creator.setText(_translate("MetaAcctXpert", "Selected:"))
        self.label_count_selected_fb_creator.setText(_translate("MetaAcctXpert", "0"))
        self.label_live_fb_creator.setText(_translate("MetaAcctXpert", "Live:"))
        self.label_live_count_fb_creator.setText(_translate("MetaAcctXpert", "0"))
        self.label_die_fb_creator.setText(_translate("MetaAcctXpert", "Die:"))
        self.label_die_count_fb_creator.setText(_translate("MetaAcctXpert", "0"))
        self.label_error_fb_creator.setText(_translate("MetaAcctXpert", "Error:"))
        self.label_error_count_fb_creator.setText(_translate("MetaAcctXpert", "0"))
        self.label_fb_verified.setText(_translate("MetaAcctXpert", "Verified:"))
        self.label_fb_verified_count.setText(_translate("MetaAcctXpert", "0"))
        self.label_fb_unverified.setText(_translate("MetaAcctXpert", "Unverified:"))
        self.label_fb_unverified_count.setText(_translate("MetaAcctXpert", "0"))
        self.setting_label.setText(_translate("MetaAcctXpert", "Settings"))
        self.cpu_ram_label_setting.setText(_translate("MetaAcctXpert", "CPU: 3.2% | RAM: 12.5%"))
        self.basic_configuration.setTitle(_translate("MetaAcctXpert", "Basic Configuration"))
        self.facebook_max_threads_label.setText(_translate("MetaAcctXpert", "No. Threads"))
        self.label_enable_proxy.setText(_translate("MetaAcctXpert", "Use Proxies"))
        self.radio_button_enable_proxy.setText(_translate("MetaAcctXpert", "On"))
        self.radio_button_disable_proxy.setText(_translate("MetaAcctXpert", "Off"))
        self.label_proxy_type.setText(_translate("MetaAcctXpert", "Proxy Type"))
        self.radio_button_http.setText(_translate("MetaAcctXpert", "HTTP"))
        self.radio_button_https.setText(_translate("MetaAcctXpert", "HTTPS"))
        self.radio_button_socks5.setText(_translate("MetaAcctXpert", "SOCKS5"))
        self.setting_otp_service_group.setTitle(_translate("MetaAcctXpert", "OTP Service"))
        self.label_wait_code_timeout.setText(_translate("MetaAcctXpert", "Code time out (s)"))
        self.label_otp_service.setText(_translate("MetaAcctXpert", "Service"))
        self.otp_service_select_options.setItemText(0, _translate("MetaAcctXpert", "Mailtm"))
        self.label_otp_service_api_key.setText(_translate("MetaAcctXpert", "API key"))
        self.label_powered_by.setText(_translate("MetaAcctXpert", "© 2025 Powered by endpointsynergy"))

        # Gắn main window
        self.main_window_instance = MetaAcctXpert

        # Kết nối toolButton
        self.toolButton_facebook.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.toolButton_settings.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))

        # khởi tạo page controller
        self.setting_controller = SettingPageController(self)
        self.facebook_controller = FacebookPageController(self)

        # Hiệu ứng nhấp nháy cho version
        opacity_effect = QGraphicsOpacityEffect(self.version)
        self.version.setGraphicsEffect(opacity_effect)

        self.version_animation = QPropertyAnimation(opacity_effect, b"opacity")
        self.version_animation.setDuration(1200)  # 1.2 giây
        self.version_animation.setStartValue(0.3)
        self.version_animation.setEndValue(1.0)
        self.version_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.version_animation.setLoopCount(-1)
        self.version_animation.start()

    def update_sys_info(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent

            # Định nghĩa nội dung text một lần duy nhất
            text_content = (
                f'<span style="color:lightgreen;">CPU: {cpu}%</span> | '
                f'<span style="color:yellow;">RAM: {ram}%</span>'
            )

            # Tạo một danh sách các label cần cập nhật
            labels_to_update = [
                self.cpu_ram_label_setting,
                self.cpu_ram_label_fb_creator
            ]

            # Vòng lặp để cập nhật từng label
            for label in labels_to_update:
                label.setText(text_content)
        except Exception as _:
            pass

    @staticmethod
    def apply_menu_style(menu: QMenu):
        menu.setStyleSheet("""
            QMenu {
                padding: 4px 6px;
                margin: 4px;
            }
            QMenu::item {
                padding: 5px 14px;
                margin: 2px 4px;
            }
            QMenu::item:selected {
                background-color: lightgray;
            }
        """)

    @staticmethod
    def custom_table_view_stylesheet() -> str:
        return """
            QTableView {
                background-color: #ffffff;
                gridline-color: #e0e0e0;
                font: 12px "Arial", sans-serif;
                color: #000;
                border: none;
                selection-background-color: rgba(70, 130, 180, 120); /* xanh steelblue nhạt */
                selection-color: #000;
            }
            
            /* Header mềm mại */
            QHeaderView::section {
                background-color: #f1f3f6;
                color: #222;
                padding: 6px 12px;
                font-weight: 600;
                font-size: 12px;
            
                border: none;                       /* bỏ toàn bộ viền */
                border-bottom: 2px solid #e0e0e0;   /* line mảnh dưới cùng */
            }


            /* Scrollbar dọc */
            QScrollBar:vertical {
                background: #f5f5f5;
                width: 8px;
                margin: 18px 0 18px 0;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: #b0b0b0;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6ba8e5, stop:1 #4a90e2
                );
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
                background: none;
            }

            /* Scrollbar ngang */
            QScrollBar:horizontal {
                background: #f5f5f5;
                height: 8px;
                margin: 0 18px 0 18px;
                border: none;
            }
            QScrollBar::handle:horizontal {
                background: #b0b0b0;
                min-width: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6ba8e5, stop:1 #4a90e2
                );
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0;
                background: none;
            }
        """

    @staticmethod
    def show_dialog(title: str = "Thông báo", message: str = ""):
        QtDialog(title=title, message=message).exec()

    def stopped_dialog(self):
        self.show_dialog(message="Tất cả tiến trình đã dừng!")
