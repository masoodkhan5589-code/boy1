import time
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from queue import Queue, Empty
from PyQt6.QtGui import QStandardItem
from typing import Dict, Any


class UiUpdater(QObject):
    update_signal = pyqtSignal(list)

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.update_signal.connect(self.manager.process_batch_update)


class TableRowProcessor(QThread):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.ui_updater = UiUpdater(manager)
        self.queue = Queue()
        self.running = True

    def enqueue(self, payload):
        self.queue.put(payload)

    def stop(self):
        self.running = False

    def _prepare_row(self, data: Dict[str, Any]):
        """Tách logic chuẩn bị hàng (mapping, tạo QStandardItem)"""
        sync_db = False
        if '_sync_db' in data:
            sync_db = data.get("_sync_db", False)
            data.pop("_sync_db", None)

        # Mapping DB keys -> headers
        mapped_data = {self.manager.key_to_header.get(k, k): v for k, v in data.items()}

        # Tìm row hiện tại trong model
        row_index = self.manager.find_row_by_value("ID Source", mapped_data.get("ID Source"))

        # Tạo QStandardItem cho từng cột, None hoặc rỗng sẽ giữ nguyên
        items = []
        for col, header in enumerate(self.manager.headers):
            val = mapped_data.get(header, None)
            if val in [None, ""]:
                items.append(None)  # giữ nguyên cột cũ
            else:
                item = QStandardItem(str(val))
                item.setEditable(False)
                items.append(item)

        # Gói items + row_index + dữ liệu gốc
        return items, row_index, data, sync_db

    def run(self):
        # Thiết lập cửa sổ batching là 200ms
        BATCH_WINDOW = 0.3
        current_batch = []
        last_update_time = time.time()

        while self.running:
            try:
                # Dùng non-blocking get với timeout ngắn để luồng không bị block hoàn toàn
                payload = self.queue.get(timeout=0.01)

                # --- Xử lý payload và thêm vào batch hiện tại ---
                if payload["action"] == "batch_update":
                    batch = payload["data"]

                    for data in batch:
                        prepared_row_item = self._prepare_row(data)
                        current_batch.append(prepared_row_item)

                self.queue.task_done()

            except Empty:
                pass  # Queue trống, tiếp tục kiểm tra điều kiện flush
            except Exception as e:
                # Xử lý lỗi nếu có
                print(f"[TableRowProcessor] Error processing payload: {e}")

            # --- Kiểm tra điều kiện FLUSH (Phát tín hiệu) ---
            time_since_last_update = time.time() - last_update_time

            # Flush khi: 1. Có dữ liệu VÀ (2. Đã hết thời gian chờ HOẶC 3. Luồng đã dừng)
            if current_batch and (time_since_last_update >= BATCH_WINDOW or not self.running):
                # Phát tín hiệu một lần cho toàn bộ batch
                self.ui_updater.update_signal.emit(current_batch)

                # Reset batch và thời gian
                current_batch = []
                last_update_time = time.time()

        # Đảm bảo xử lý nốt các mục còn lại nếu còn
        if current_batch:
            self.ui_updater.update_signal.emit(current_batch)
