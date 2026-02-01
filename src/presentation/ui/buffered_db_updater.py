import threading
import time
import json
import os
from queue import Queue, Empty
from sqlalchemy.exc import SQLAlchemyError
from src.infrastructure.database import TableWidgetDataModel


class BufferedDBUpdater(threading.Thread):
    def __init__(self, session_factory, interval_sec: float = 3.0, persist_file: str = "db_queue.json"):
        super().__init__()
        self.session_factory = session_factory
        self.interval_sec = interval_sec
        self.queue = Queue()
        self._stop_flag = threading.Event()
        self.persist_file = persist_file

        # Load queue từ file nếu tồn tại
        if os.path.exists(self.persist_file):
            try:
                with open(self.persist_file, "r", encoding="utf-8") as f:
                    items = json.load(f)
                    for item in items:
                        self.queue.put(item)
            except Exception as e:
                print(f"[Warning] Failed to load persisted queue: {e}")

    # ===============================
    # Thread lifecycle
    # ===============================
    def run(self):
        while not self._stop_flag.is_set():
            time.sleep(self.interval_sec)
            self.flush()

    def stop(self):
        """Dừng thread và flush lần cuối"""
        self._stop_flag.set()
        self.flush()
        self._persist_queue()

    # ===============================
    # Public API
    # ===============================
    def add_update(self, data: dict):
        """Single row update (backward-compatible)"""
        self.enqueue({
            "action": "update",
            "table": "TableWidgetDataModel",
            "data": data
        })

    def enqueue(self, payload: dict):
        """Thêm payload (update / batch_update / batch_delete)"""
        self.queue.put(payload)
        self._persist_queue()

    # ===============================
    # Core flush logic
    # ===============================
    def flush(self):
        if self.queue.empty():
            return

        session = self.session_factory()
        try:
            pending_payloads = []
            while True:
                try:
                    pending_payloads.append(self.queue.get_nowait())
                except Empty:
                    break

            for payload in pending_payloads:
                action = payload.get("action")
                data = payload.get("data")
                if not data:
                    continue

                if action == "update":
                    self._handle_single_update(session, data)
                elif action == "batch_update" and isinstance(data, list):
                    self._handle_batch_update(session, data)
                elif action == "batch_delete" and isinstance(data, list):
                    self._handle_batch_delete(session, data)

            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"[Error] BufferedDBUpdater.flush: {e}")
        finally:
            session.close()
            self._persist_queue()  # persist queue còn sót nếu crash giữa chừng

    # ===============================
    # Handlers
    # ===============================
    @staticmethod
    def _handle_single_update(session, data: dict):
        id_source = data.get("id_source")
        if not id_source:
            return
        instance = session.query(TableWidgetDataModel).filter_by(id_source=id_source).first()
        if instance:
            for key, value in data.items():
                if hasattr(instance, key) and value not in [None, ""]:
                    setattr(instance, key, value)
        else:
            session.add(TableWidgetDataModel(**data))

    @staticmethod
    def _handle_batch_update(session, rows: list[dict]):
        for data in rows:
            BufferedDBUpdater._handle_single_update(session, data)

    @staticmethod
    def _handle_batch_delete(session, data_list: list[dict]):
        if not data_list:
            return
        ids = [d["id_source"] for d in data_list if "id_source" in d]
        if ids:
            session.query(TableWidgetDataModel).filter(TableWidgetDataModel.id_source.in_(ids)).delete(
                synchronize_session=False
            )

    # ===============================
    # Crash-safe persistence
    # ===============================
    def _persist_queue(self):
        """Lưu queue ra file JSON"""
        items = list(self.queue.queue)
        try:
            with open(self.persist_file + ".tmp", "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
            os.replace(self.persist_file + ".tmp", self.persist_file)
        except Exception as e:
            print(f"[Warning] Failed to persist queue: {e}")
