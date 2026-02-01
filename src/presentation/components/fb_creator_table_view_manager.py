import atexit
from typing import List, Dict, Any, Union
from PyQt6.QtCore import QModelIndex, QCoreApplication, pyqtSignal, QObject
from PyQt6.QtGui import QColor, QBrush, QStandardItem
from sqlalchemy.exc import SQLAlchemyError
from PyQt6.QtWidgets import QDialogButtonBox, QDialog, QVBoxLayout, QLabel, QLineEdit

from src.infrastructure.database import SessionLocal
from src.common.status_constants import StatusConstants
from src.infrastructure.database import TableWidgetDataModel
from src.presentation.components.base_table_view_manager import BaseTableViewManager
from src.presentation.ui.buffered_db_updater import BufferedDBUpdater
from src.presentation.ui.table_row_processor import TableRowProcessor


class FbCreatorTableViewManager(BaseTableViewManager, QObject):

    modelUpdated = pyqtSignal()
    selectedUpated = pyqtSignal()

    def __init__(self, table_view, headers: List[str]):
        super().__init__(table_view, headers)
        QObject.__init__(self)

        # Mapping snake_case (DB) -> Title Case (UI)
        self.key_to_header = {
            "id_source": "ID Source",
            "uid": "UID",
            "password": "Password",
            "twofactor": "Two Factor",
            "cookie": "Cookie",
            "bearer_token": "Access Token",
            "fullname": "Full Name",
            "contact": "Contact",
            "otp": "OTP",
            "create_date": "Create Date",
            "proxy": "Proxy",
            "ip_address": "IP Address",
            "device": "Device",
            "is_verified": "Verified Status",
            "account_status": "Account Status",
            "total_time": "Total Time",
            "status": "Status"
        }
        # Reverse mapping Title Case -> snake_case
        self.header_to_key = {v: k for k, v in self.key_to_header.items()}

        # Khởi tạo updater nền
        self.db_updater = BufferedDBUpdater(SessionLocal, interval_sec=2.0)
        self.db_updater.start()

        # Gắn auto-stop khi app thoát (2 lớp bảo hiểm)
        app = QCoreApplication.instance()
        if app:
            app.aboutToQuit.connect(self.db_updater.stop)
        atexit.register(self.db_updater.stop)

        self.ui_queue = TableRowProcessor(self)
        self.ui_queue.start()

    def __set_color(self, row: int):
        """Tô màu dòng dựa vào trạng thái (tối ưu tốc độ)"""
        model = self.model
        if row >= model.rowCount():
            return

        # Chỉ tìm index 1 lần, nếu chưa truyền sẵn
        try:
            account_status_col = self.headers.index("Account Status")
            status_col = self.headers.index("Status")
        except ValueError:
            print("[Error] 'Account Status' column not found in headers")
            return

        account_status_item = model.item(row, account_status_col)
        status_item = model.item(row, status_col)

        account_text = ""
        status_alt_text = ""

        # 1. Kiểm tra và lấy văn bản từ Account Status
        if account_status_item:
            account_text = account_status_item.text().strip()

        # 2. Kiểm tra và lấy văn bản từ Status
        if status_item:
            status_alt_text = status_item.text().strip()

        # 3. Kết hợp logic ưu tiên
        status_text = account_text if account_text else status_alt_text

        # Dùng dict để map status -> color, tránh if/elif nhiều lần
        RED = (178, 34, 34)
        GREEN = (0, 128, 0)
        ORANGE = (255, 165, 0)

        status_color_map = {
            StatusConstants.ACCOUNT_DISABLED: RED,
            StatusConstants.RECOVERY_FAILED: RED,
            StatusConstants.ACCOUNT_LIVE: GREEN,
            StatusConstants.RECOVERY_SUCCESSFUL: GREEN,
            "": ORANGE,
        }

        r, g, b = status_color_map.get(status_text, (0, 0, 0))
        brush = QBrush(QColor(r, g, b))

        # Tô toàn bộ dòng
        for col in range(model.columnCount()):
            item = model.item(row, col)
            if item:
                item.setForeground(brush)

    # ==========================================================
    # HÀM CHÍNH — hỗ trợ Dict hoặc List[Dict]
    # ==========================================================
    def add_or_update_row(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], sync_db: bool = True):
        """Chỉ push dữ liệu vào queue, không update trực tiếp UI"""
        if not data:
            return

        rows = data if isinstance(data, list) else [data]

        for d in rows:
            d["_sync_db"] = d.get("sync_db", sync_db)

        self.ui_queue.enqueue({
            "action": "batch_update",
            "data": rows,
        })

    def process_batch_update(self, prepared_rows, sync_db=True):
        model = self.model
        # model.blockSignals(True)
        # self.table_view.setUpdatesEnabled(False)

        rows_to_sync = []  # lưu dữ liệu gốc để sync DB

        for items, row_index, original_data, sync_db in prepared_rows:

            if sync_db:
                rows_to_sync.append(original_data)

            if row_index == -1:
                new_items = [item if item is not None else QStandardItem("") for item in items]
                for item in new_items:
                    item.setEditable(False)
                model.appendRow(new_items)
                color_row = model.rowCount() - 1
            else:
                # nếu row đã tồn tại, chỉ update cột có dữ liệu
                for col, item in enumerate(items):
                    if item is not None:  # chỉ update nếu có dữ liệu
                        model.setItem(row_index, col, item)
                color_row = row_index

            self.__set_color(color_row)

        # model.blockSignals(False)
        # self.table_view.setUpdatesEnabled(True)
        # self.table_view.viewport().update()
        self.modelUpdated.emit()

        if sync_db and rows_to_sync:
            self.db_updater.enqueue({
                "action": "batch_update",
                "table": "TableWidgetDataModel",
                "data": rows_to_sync
            })

    # ==========================================================
    def remove_row_by_id_source(self, id_sources: Union[List[str], str]):
        """Xoá nhiều row cùng lúc mà không lag, giữ header"""
        if isinstance(id_sources, str):
            id_sources = [id_sources]

        if not id_sources:
            return

        source_model = self.model
        if hasattr(source_model, 'sourceModel'):
            source_model = source_model.sourceModel()

        # 1. Bật lại blockSignals để tránh lag khi xóa hàng loạt
        source_model.blockSignals(True)
        self.table_view.setUpdatesEnabled(False)

        id_source_col = self.headers.index("ID Source")
        rows_to_remove = []

        # Tìm row thực sự cần xoá
        for row in range(source_model.rowCount()):
            item = source_model.item(row, id_source_col)
            if item and item.text() in id_sources:
                rows_to_remove.append(row)

        # Xoá từ dưới lên để tránh shift index
        for row in sorted(rows_to_remove, reverse=True):
            source_model.removeRow(row)

        # 2. Tắt chặn tín hiệu
        source_model.blockSignals(False)

        self.table_view.setUpdatesEnabled(True)
        self.table_view.viewport().update()
        self.selectedUpated.emit()
        self.modelUpdated.emit()

        # Enqueue DB
        self.db_updater.enqueue({
            "action": "batch_delete",
            "table": "TableWidgetDataModel",
            "data": [{"id_source": id_source} for id_source in id_sources]
        })

    def find_row_by_value(self, header: str, value: Any) -> int:
        """Tìm index của row theo giá trị cột"""
        if header not in self.headers:
            return -1
        col_index = self.headers.index(header)
        for row in range(self.model.rowCount()):
            item = self.model.item(row, col_index)
            if item and item.text() == str(value):
                return row
        return -1

    def load_all_from_db(self):
        """Load toàn bộ DB vào bảng khi khởi động"""
        self.clean_table()
        try:
            instances = self.session.query(TableWidgetDataModel).all()
            data_list = [
                {col.name: getattr(instance, col.name) for col in TableWidgetDataModel.__table__.columns}
                for instance in instances
            ]
            self.add_or_update_row(data_list, sync_db=False)
        except SQLAlchemyError as e:
            print(f"[Error] load_all_from_db: {e}")

    def handle_double_click(self, index: QModelIndex):
        if not index.isValid():
            return

        old_value = index.data()
        dialog = QDialog(self.table_view)
        dialog.setWindowTitle("Chỉnh sửa ô")
        dialog.setModal(True)

        layout = QVBoxLayout()
        label = QLabel("Giá trị mới:")
        label.setStyleSheet("border: 0;")
        line_edit = QLineEdit()
        line_edit.setText(str(old_value))
        layout.addWidget(label)
        layout.addWidget(line_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(button_box)
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)

        dialog.setStyleSheet("""
            QDialog { background-color: #fff; color: #000; }
            QLabel { font-size: 14px; background-color: transparent; color: #000; }
            QLineEdit { background-color: #3c3c3c; color: #fff; border: 1px solid #555; padding: 5px; }
        """)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: #fff;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #388e3c; }
        """)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #c62828;
                color: #fff;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #d32f2f; }
        """)

        dialog.setLayout(layout)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_value = line_edit.text()
            if new_value == old_value:
                return
            row_index = index.row()
            data = self.get_row_data(row_index)
            db_key = self.header_to_key.get(self.headers[index.column()], None)
            if db_key:
                data[db_key] = new_value
                self.add_or_update_row(data)
