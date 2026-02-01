import re
import uuid
from typing import Dict, Any, Union

from PyQt6.QtCore import QObject, Qt, QThreadPool
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMenu, QFileDialog, QApplication

from src.common.logger import logger
from src.common.status_constants import StatusConstants
from src.domain.dtos.table_widget_payload_data import TableWidgetPayloadData
from src.domain.enums.copy_options import CopyOptions
from src.infrastructure.files.file_reader import FileReader
from src.infrastructure.serializers.table_widget_data_serializer import TableWidgetDataSerializer
from src.presentation.components.fb_creator_table_view_manager import FbCreatorTableViewManager
from src.presentation.components.gui_controller import GUIController


class FacebookPageController(QObject):

    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.gui_controller: GUIController = ui.gui_controller

        self.is_running = False
        self.table_manager: FbCreatorTableViewManager

        self.threadpool = QThreadPool()

        # Khởi tạo table view
        self._table_view()

    def _table_view(self):

        # Khởi tạo table manager
        headers = [
            "ID Source", "UID", "Password", "Two Factor", "Cookie", "Access Token", "Full Name", "Contact", "OTP",
            "Create Date", "Proxy", "IP Address", "Device", "Verified Status", "Account Status", "Total Time", "Status"
        ]
        self.table_manager = FbCreatorTableViewManager(table_view=self.ui.facebook_creator_table_view, headers=headers)

        # Ẩn số thứ tự
        self.ui.facebook_creator_table_view.verticalHeader().setVisible(False)

        # Table Action
        self.ui.facebook_creator_table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.facebook_creator_table_view.customContextMenuRequested.connect(self._show_menu_when_right_clicked)

        # Double click để sửa dữ liệu
        self.ui.facebook_creator_table_view.doubleClicked.connect(self.table_manager.handle_double_click)

        # Set width of status column
        self.ui.facebook_creator_table_view.setColumnHidden(0, True)

        # Load setting
        self._initialization_data_table_widget()

        # Lưu width của cột
        self.ui.facebook_creator_table_view.horizontalHeader().sectionResized.connect(
            self.table_manager.save_column_widths
        )

        # Select count, total rows
        self.ui.facebook_creator_table_view.selectionModel().selectionChanged.connect(self._count_selected_rows)
        self.table_manager.selectedUpated.connect(self._count_selected_rows)

        # Counter
        self.table_manager.modelUpdated.connect(self._update_count_bar)

        # Override table view stylesheet
        self.ui.facebook_creator_table_view.setStyleSheet(self.ui.custom_table_view_stylesheet())

    def _update_count_bar(self, error_count: int = 0):
        total_count = self.table_manager.get_count_by_header_value("ID Source")
        verified_count = self.table_manager.get_count_by_header_value("Verified Status", StatusConstants.VERIFIED)
        unverified_count = self.table_manager.get_count_by_header_value("Verified Status", StatusConstants.UNVERIFIED)
        checkpoint_count = self.table_manager.get_count_by_header_value("Account Status",
                                                                        StatusConstants.ACCOUNT_DISABLED)
        live_count = self.table_manager.get_count_by_header_value("Account Status", StatusConstants.ACCOUNT_LIVE)

        self.ui.label_count_all_fb_creator.setText(str(total_count))
        self.ui.label_fb_verified_count.setText(str(verified_count))
        self.ui.label_fb_unverified_count.setText(str(unverified_count))
        self.ui.label_die_count_fb_creator.setText(str(checkpoint_count))
        self.ui.label_live_count_fb_creator.setText(str(live_count))

        if error_count:
            self.ui.label_error_count_fb_creator.setText(str(error_count))

    def _show_menu_when_right_clicked(self, position):
        self.context_menu = QMenu()
        self.context_menu.setContentsMargins(10, 5, 10, 5)

        # === Submenu "Start" ===
        start_menu = QMenu()
        login_api_android_action = QAction("Login API Android", self.context_menu)
        start_menu.addAction(login_api_android_action)

        verify_account_api_android_action = QAction("Verify account", self.context_menu)
        start_menu.addAction(verify_account_api_android_action)

        verify_without_submit_code_api_android_action = QAction("Verify account (no code submission)",
                                                                self.context_menu)
        start_menu.addAction(verify_without_submit_code_api_android_action)

        forgot_password_action = QAction("Forgot password", self.context_menu)
        start_menu.addAction(forgot_password_action)

        start_action = QAction("Start", self.context_menu)
        start_action.setIcon(QIcon(":/images/statics/start.png"))
        start_action.setIconVisibleInMenu(True)
        start_action.setMenu(start_menu)
        self.context_menu.addAction(start_action)

        # === Stop ===
        stop_action = QAction("Stop", self.context_menu)
        stop_action.setIcon(QIcon(":/images/statics/stop.png"))
        stop_action.setIconVisibleInMenu(True)
        self.context_menu.addAction(stop_action)

        self.context_menu.addSeparator()

        # === Submenu "Copy" ===
        copy_menu = QMenu()
        self.copy_actions = {}
        for copy_type in CopyOptions:
            action = QAction(copy_type.value, self.context_menu)
            copy_menu.addAction(action)
            self.copy_actions[action] = copy_type

        copy_action = QAction("Copy", self.context_menu)
        copy_action.setIcon(QIcon(":/images/statics/copy.png"))
        copy_action.setIconVisibleInMenu(True)
        copy_action.setMenu(copy_menu)
        self.context_menu.addAction(copy_action)

        self.context_menu.addSeparator()

        # === Submenu "Account" ===
        account_menu = QMenu()
        check_live_uid_action = QAction("Check live UID", self.context_menu)
        account_menu.addAction(check_live_uid_action)

        check_info_token = QAction("Check info token", self.context_menu)
        account_menu.addAction(check_info_token)

        account_action = QAction("Account", self.context_menu)
        account_action.setIcon(QIcon(":/images/statics/account.png"))
        account_action.setIconVisibleInMenu(True)
        account_action.setMenu(account_menu)
        self.context_menu.addAction(account_action)

        self.context_menu.addSeparator()

        # === Import ===
        import_menu = QMenu()
        import_account_action = QAction("Import Accounts", self.context_menu)
        import_menu.addAction(import_account_action)

        import_contact_action = QAction("Import Contacts", self.context_menu)
        import_menu.addAction(import_contact_action)

        import_action = QAction("Import", self.context_menu)
        import_action.setIcon(QIcon(":/images/statics/import.png"))
        import_action.setIconVisibleInMenu(True)
        import_action.setMenu(import_menu)
        self.context_menu.addAction(import_action)

        self.context_menu.addSeparator()

        # === Refresh ===
        refresh_action = QAction("Refresh", self.context_menu)
        refresh_action.setIcon(QIcon(":/images/statics/refresh.png"))
        refresh_action.setIconVisibleInMenu(True)
        self.context_menu.addAction(refresh_action)

        self.context_menu.addSeparator()

        # === Delete ===
        delete_row_action = QAction("Delete row", self.context_menu)
        delete_row_action.setIcon(QIcon(":/images/statics/delete.png"))
        delete_row_action.setIconVisibleInMenu(True)
        self.context_menu.addAction(delete_row_action)

        # === Style ===
        self.ui.apply_menu_style(self.context_menu)
        self.ui.apply_menu_style(copy_menu)
        self.ui.apply_menu_style(start_menu)
        self.ui.apply_menu_style(account_menu)
        self.ui.apply_menu_style(import_menu)

        # === Show menu at cursor position ===
        action = self.context_menu.exec(self.ui.facebook_creator_table_view.viewport().mapToGlobal(position))

        # === Handle actions ===
        if action in self.copy_actions:
            copy_type = self.copy_actions[action]
            self._copy_item(copy_type)

        elif action == check_live_uid_action:
            self._check_live_account()

        elif action == check_info_token:
            self._check_info_token()

        elif action == login_api_android_action:
            self._login_api_android_action()

        elif action == verify_account_api_android_action:
            self._verify_account_api_android_action()

        elif action == verify_without_submit_code_api_android_action:
            self._verify_without_submit_code_api_android_action()

        elif action in [import_account_action, import_contact_action]:
            self._import_accounts(import_contact=bool(action == import_contact_action))

        elif action == forgot_password_action:
            self._forgot_password_action()

        elif action == refresh_action:
            self._refresh_action()

        elif action == delete_row_action:
            self._delete_selected_items()

        elif action == stop_action:
            self._handle_stop_button()

    def _handle_stop_button(self):
        if not self.is_running:
            return

        if not self.table_manager.show_confirm_dialog(
                self.ui.main_window_instance,
                "<span style='color: #000; font-weight: bold;'>Bạn có muốn dừng toàn bộ tiến trình?</span>",
                "Xác nhận"
        ):
            return

        self.is_running = False

        # Dừng QProcessWorker hiện tại nếu đang chạy
        if self.gui_controller.process is not None and self.gui_controller.process.isRunning():
            self.gui_controller.process.requestInterruption()
            self.gui_controller.process.quit()

    def _count_selected_rows(self):
        selected_indexes = self.ui.facebook_creator_table_view.selectionModel().selectedRows()
        count = len(selected_indexes)
        self.ui.label_count_selected_fb_creator.setText(str(count))

    def _get_select_items(self) -> list[str]:
        seen = set()
        filtered_items = []

        selected_indexes = self.ui.facebook_creator_table_view.selectionModel().selectedRows()

        for index in selected_indexes:
            # Khi không dùng proxy_model, chỉ mục (index) từ view
            # chính là chỉ mục của model gốc.
            row = index.row()  # Lấy thẳng chỉ mục hàng

            row_data = []
            for col in range(self.table_manager.model.columnCount()):
                # Dùng row_data để lấy dữ liệu từ model gốc
                item = self.table_manager.model.item(row, col)
                row_data.append(item.text() if item else "")

            sep = "|"
            item_str = sep.join(row_data)

            # Đảm bảo không có hàng trùng lặp (ví dụ: khi chọn nhiều ô trên cùng một dòng)
            if item_str not in seen:
                seen.add(item_str)
                filtered_items.append(item_str)

        return filtered_items

    def _check_live_account(self):
        selected_items = self._get_select_items()
        self.gui_controller.handle_check_live_facebook_account(self.add_or_update_row, selected_items)

    def _check_info_token(self):
        selected_items = self._get_select_items()
        self.gui_controller.handle_check_info_token(self.add_or_update_row, selected_items)

    def _login_api_android_action(self):
        selected_items = self._get_select_items()
        self.gui_controller.handle_login(
            add_or_update_row=self.add_or_update_row,
            get_is_running=self.get_is_running,
            set_is_running=self.set_is_running,
            update_count_bar=self._update_count_bar,
            selected_items=selected_items,
        )

    def _verify_account_api_android_action(self):
        selected_items = self._get_select_items()
        self.gui_controller.handle_verify_account_api_android(
            add_or_update_row=self.add_or_update_row,
            get_is_running=self.get_is_running,
            set_is_running=self.set_is_running,
            update_count_bar=self._update_count_bar,
            selected_items=selected_items,
        )

    def _verify_without_submit_code_api_android_action(self):
        selected_items = self._get_select_items()
        self.gui_controller.handle_verify_without_submit_code_api_android_action(
            add_or_update_row=self.add_or_update_row,
            get_is_running=self.get_is_running,
            set_is_running=self.set_is_running,
            update_count_bar=self._update_count_bar,
            selected_items=selected_items,
        )

    def _handle_delete_finished(self, delete_count: int):
        """
        Xử lý sau khi DeleteWorker hoàn thành việc xóa DB trên luồng nền.
        Chạy trên luồng chính (UI Thread).
        """
        if delete_count > 0:
            # Chỉ hiển thị thông báo về việc xóa DB nếu có hàng nào đó được xóa
            self.ui.show_dialog(
                title="Xóa Thành Công",
                message=f"Đã xóa thành công {delete_count} hàng khỏi Cơ sở dữ liệu."
            )

        # Cập nhật lại thanh đếm (vì số lượng hàng trong DB đã thay đổi)
        self._update_count_bar()

        self.delete_worker = None  # Dọn dẹp Worker

    def _delete_selected_items(self):
        selected_items = self._get_select_items()

        if not selected_items:
            return

        # Yêu cầu xác nhận xóa từ người dùng
        if not self.table_manager.show_confirm_dialog(
                self.ui.main_window_instance,
                f"<span style='color: #000; font-weight: bold;'>Bạn có chắc chắn muốn xóa {len(selected_items)} dòng đã chọn không?</span>",
                "Xác nhận xóa"
        ):
            return

        id_sources_to_delete = []

        for item in selected_items:
            try:
                id_source = item.split('|')[0]
                id_sources_to_delete.append(id_source)
            except IndexError:
                continue

        if id_sources_to_delete:
            self.table_manager.remove_row_by_id_source(id_sources_to_delete)

    def _copy_item(self, copy_type: CopyOptions):
        selected_items = self._get_select_items()
        if not selected_items:
            return

        # Xử lý sao chép theo copy_type
        copied_texts = []
        for item in selected_items:
            data_obj = TableWidgetDataSerializer.from_pipe_string(item)
            if copy_type == CopyOptions.COPY_TYPE_1:
                copied_texts.append(data_obj.uid)
            elif copy_type == CopyOptions.COPY_TYPE_2:
                copied_texts.append(f"{data_obj.uid}|{data_obj.password}")
            elif copy_type == CopyOptions.COPY_TYPE_3:
                copied_texts.append(f"{data_obj.uid}|{data_obj.password}|{data_obj.twofactor}")
            elif copy_type == CopyOptions.COPY_TYPE_4:
                copied_texts.append(f"{data_obj.uid}|{data_obj.password}|{data_obj.twofactor}|{data_obj.cookie}")
            elif copy_type == CopyOptions.COPY_TYPE_5:
                copied_texts.append(
                    f"{data_obj.uid}|{data_obj.password}|{data_obj.twofactor}|{data_obj.cookie}|{data_obj.bearer_token}")
            elif copy_type == CopyOptions.COPY_TYPE_6:
                copied_texts.append(f"{data_obj.uid}|{data_obj.password}|{data_obj.cookie}|{data_obj.bearer_token}")
            elif copy_type == CopyOptions.COPY_TYPE_7:
                copied_texts.append(
                    f"{data_obj.uid}|{data_obj.password}|{data_obj.twofactor}|{data_obj.cookie}|{data_obj.bearer_token}|{data_obj.contact}")
            elif copy_type == CopyOptions.COPY_TYPE_8:
                copied_texts.append(
                    f"{data_obj.uid}|{data_obj.password}|{data_obj.cookie}|{data_obj.bearer_token}|{data_obj.contact}")
            elif copy_type == CopyOptions.COPY_TYPE_9:
                copied_texts.append(
                    f"{data_obj.uid}|{data_obj.password}|{data_obj.cookie}|{data_obj.bearer_token}|{data_obj.contact}|{data_obj.otp}")

        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join(copied_texts))
        self.ui.show_dialog(message=f"Copied {len(copied_texts)} lines to clipboard.")

    def _import_accounts(self, import_contact: bool = False):
        """
        Import tài khoản hoặc danh sách contact vào bảng.
        Nếu import_contact=True thì chỉ lấy contact và thêm vào TableWidgetData(contact=...).
        """

        def is_cookie(s: str) -> bool:
            return "c_user=" in s

        def is_bearer_token(s: str) -> bool:
            return "EAA" in s

        def is_twofactor_key(s: str) -> bool:
            return re.fullmatch(r'[A-Z2-7]{16,32}', s) is not None

        def pad_fields(fields: list[str], target_len: int, default: str = "") -> list[str]:
            return fields + [default] * (target_len - len(fields))

        import_count = 0

        try:
            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
            file_dialog.setNameFilter("Text Files (*.txt);;All Files (*)")

            selected_file, _ = file_dialog.getOpenFileName(
                self.ui.main_window_instance, "Open TXT File", "", "Text Files (*.txt);;All Files (*)"
            )

            if not selected_file:
                return

            file_lines = FileReader(file_path=selected_file).read_lines()

            for line in file_lines:
                line = line.strip()
                if not line:
                    continue

                # ========== TRƯỜNG HỢP IMPORT CONTACT ========== #
                if import_contact:
                    contact = line.split('|')[0].strip()
                    if not contact:
                        continue

                    account_data = TableWidgetPayloadData(
                        id_source=str(uuid.uuid4()),
                        uid="",
                        password="",
                        twofactor="",
                        cookie="",
                        bearer_token="",
                        fullname="",
                        contact=contact,
                        create_date="",
                        proxy="",
                        ip_address="",
                        status=StatusConstants.ACCOUNT_LOADED
                    )
                    self.add_or_update_row(vars(account_data))
                    import_count += 1
                    continue

                # ========== TRƯỜNG HỢP IMPORT ACCOUNT BÌNH THƯỜNG ========== #
                raw_fields = [f.strip() for f in str(line).split('|')]
                fields = pad_fields(raw_fields, 10)

                cookie = next((f for f in fields if is_cookie(f)), None)
                bearer_token = next((f for f in fields if is_bearer_token(f)), None)
                twofactor = next((f for f in fields if is_twofactor_key(f)), None)

                remaining_fields = [f for f in fields if f not in {cookie, bearer_token, twofactor}]
                remaining_fields = pad_fields(remaining_fields, 7)

                account_data = TableWidgetPayloadData(
                    id_source=str(uuid.uuid4()),
                    uid=remaining_fields[0],
                    password=remaining_fields[1],
                    twofactor=twofactor or "",
                    cookie=cookie or "",
                    bearer_token=bearer_token or "",
                    fullname=remaining_fields[2],
                    contact=remaining_fields[3],
                    create_date=remaining_fields[4],
                    proxy=remaining_fields[5],
                    ip_address=remaining_fields[6],
                    status=StatusConstants.ACCOUNT_LOADED
                )

                self.add_or_update_row(vars(account_data))
                import_count += 1

        except FileNotFoundError:
            logger.warning("File not found or not selected.")
        except Exception as e:
            logger.error(f"Unexpected error while importing accounts: {e}")
        finally:
            self.ui.show_dialog(
                title="Import Completed!",
                message=f"Imported: {import_count}"
            )

    def _forgot_password_action(self):
        selected_items = self._get_select_items()
        self.gui_controller.handle_forgot_password_action(
            add_or_update_row=self.add_or_update_row,
            get_is_running=self.get_is_running,
            set_is_running=self.set_is_running,
            update_count_bar=self._update_count_bar,
            selected_items=selected_items,
        )

    def _refresh_action(self):
        self.table_manager.load_all_from_db()
        self._update_count_bar()
        self.ui.facebook_creator_table_view.model().sort(0, Qt.SortOrder.AscendingOrder)

    def _initialization_data_table_widget(self):
        try:
            self.ui.facebook_creator_table_view.setUpdatesEnabled(False)
            self.table_manager.load_all_from_db()

            restored = self.table_manager.restore_column_widths()
            self._update_count_bar()
            self.ui.facebook_creator_table_view.model().sort(-1)

            if not restored:
                self.ui.facebook_creator_table_view.resizeColumnsToContents()

        except Exception as e:
            logger.warning(f"[TableView Init] Error in _initialization_data_table_widget: {e}")

        finally:
            self.ui.facebook_creator_table_view.setUpdatesEnabled(True)
            self.ui.facebook_creator_table_view.viewport().update()

    def add_or_update_row(self, data: Union[Dict[str, Any], list[Dict[str, Any]]]):
        self.table_manager.add_or_update_row(data)

    def get_is_running(self):
        return self.is_running

    def set_is_running(self, is_running):
        self.is_running = is_running
