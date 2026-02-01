from dataclasses import dataclass
from typing import Optional

from src.domain.dtos.setting_loader_data import SettingLoaderData


@dataclass
class FbKatanaVerifyAccountData:
    id_source: str
    fb_user_id: str
    fb_password: str
    fb_access_token: str
    device_id: str
    language: str
    settings: SettingLoaderData
    response_to_table_widget: Optional[callable] = None
    time_out: int = 90
