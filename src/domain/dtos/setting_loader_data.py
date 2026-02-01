from dataclasses import dataclass
from typing import Optional

from src.infrastructure.database import Setting


@dataclass
class SettingLoaderData:
    global_setting: Optional[Setting] = None
