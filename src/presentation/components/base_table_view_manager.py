from typing import List, Dict, Any
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QStandardItemModel

from PyQt6.QtWidgets import QMessageBox
from src.infrastructure.database import SessionLocal


class BaseTableViewManager:
    def __init__(self, table_view, headers: List[str]):
        self.session = SessionLocal()

        self.table_view = table_view
        self.headers = headers

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(self.headers)

        self.table_view.setSortingEnabled(True)
        self.table_view.setModel(self.model)
        self.table_view.setSelectionBehavior(self.table_view.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(self.table_view.SelectionMode.ExtendedSelection)
        self.table_view.horizontalHeader().setStretchLastSection(True)

        self.key_to_header = {}
        self.header_to_key = {}

    def get_row_data(self, row_index: int) -> Dict[str, Any]:
        """Lấy dữ liệu 1 dòng từ bảng"""
        if 0 <= row_index < self.model.rowCount():
            data = {}
            for col_index, header in enumerate(self.headers):
                item = self.model.item(row_index, col_index)
                db_key = self.header_to_key.get(header, header)
                data[db_key] = item.text() if item else ""
            return data
        return {}

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

    def save_column_widths(self):
        settings = QSettings("FbCreatorTool", "TableColumnWidths")
        for col in range(self.model.columnCount()):
            width = self.table_view.columnWidth(col)
            settings.setValue(f"column_width_{col}", width)

    def restore_column_widths(self):
        settings = QSettings("FbCreatorTool", "TableColumnWidths")
        restored = False
        for col in range(self.model.columnCount()):
            width = settings.value(f"column_width_{col}", type=int)
            if width:
                if width < 100:
                    width = 100

                self.table_view.setColumnWidth(col, width)
                restored = True
        return restored

    @staticmethod
    def show_confirm_dialog(main_window_instance, text, title="Xác nhận"):
        msg_box = QMessageBox(main_window_instance)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Icon.Question)

        yes_button = msg_box.addButton("Yes", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("No", QMessageBox.ButtonRole.NoRole)

        # Style
        yes_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;  /* Green */
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)

        no_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;  /* Red */
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)

        msg_box.exec()
        return msg_box.clickedButton() == yes_button

    def get_count_by_header_value(self, header: str, value: Any = None) -> int:
        """Trả về số lượng dòng có giá trị value tại cột header.
        - value:
            + None / "" / [] / {}: đếm tất cả dòng có dữ liệu tại cột.
            + str: đếm dòng có giá trị đúng bằng chuỗi.
            + list[str]: đếm dòng có giá trị nằm trong list.
        """
        if header not in self.headers:
            print(f"[Error] Header '{header}' không tồn tại.")
            return 0

        col_index = self.headers.index(header)
        count = 0

        for row in range(self.model.rowCount()):
            item = self.model.item(row, col_index)
            text = item.text().strip() if item else ""

            if value in [None, "", [], {}]:
                if text:
                    count += 1
            elif isinstance(value, list):
                if text in map(str, value):
                    count += 1
            else:
                if text == str(value):
                    count += 1

        return count

    def clean_table(self):
        self.model.removeRows(0, self.model.rowCount())  # xoá bảng
