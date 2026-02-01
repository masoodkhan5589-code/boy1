import threading
import time
from typing import Optional

from src.domain.dtos.setting_loader_data import SettingLoaderData
from src.infrastructure.database import SessionLocal, Setting


class ConfigurationService:
    """
    Quản lý việc tải, lưu và cập nhật cài đặt ứng dụng một cách tập trung.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ConfigurationService, cls).__new__(cls)
                cls._instance._init()
        return cls._instance

    def _init(self):
        self._current_settings: Optional[SettingLoaderData] = None
        self._update_interval: int = 30
        self._thread = threading.Thread(target=self._run_update_loop, daemon=True)
        self._thread.start()

    def _run_update_loop(self):
        while True:
            self.load_settings_from_db()
            time.sleep(self._update_interval)

    def load_settings_from_db(self):
        with SessionLocal() as session:
            setting = session.query(Setting).first()

            if not setting:
                setting = None

            self._current_settings = SettingLoaderData(global_setting=setting)

    def get_settings(self) -> SettingLoaderData:
        if self._current_settings is None:
            self.load_settings_from_db()
        return self._current_settings

    def save_settings_to_db(self, setting_data: Setting):
        with SessionLocal() as session:
            # 1. Kiểm tra kiểu dữ liệu để chọn đúng bảng
            if isinstance(setting_data, Setting):
                model_class = Setting
            else:
                print("Lỗi: Kiểu dữ liệu không hợp lệ")
                return

            # 2. Tìm kiếm đối tượng đã tồn tại
            existing_data = session.query(model_class).first()

            if existing_data is None:
                # Nếu chưa tồn tại, thêm mới
                session.add(setting_data)
            else:
                # Nếu đã tồn tại, cập nhật các thuộc tính
                for field in setting_data.__table__.columns.keys():
                    if field == "id":
                        continue
                    # Đảm bảo thuộc tính tồn tại trong cả hai đối tượng trước khi cập nhật
                    if hasattr(setting_data, field) and hasattr(existing_data, field):
                        setattr(existing_data, field, getattr(setting_data, field))

            session.commit()

            # Cập nhật cài đặt ngay lập tức sau khi lưu
            self.load_settings_from_db()
