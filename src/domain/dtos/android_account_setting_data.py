from dataclasses import dataclass

from src.common.status_constants import StatusConstants


@dataclass
class AndroidAccountSettingData:
    status_manager: StatusConstants
    time_out: int = 60
