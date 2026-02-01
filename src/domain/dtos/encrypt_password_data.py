from dataclasses import dataclass
from typing import Optional


@dataclass
class EncryptPasswordData:
    password: str
    country_code: str
    family_device_id: str
    proxy: Optional[str] = None
