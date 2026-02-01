from dataclasses import dataclass
from typing import Optional


@dataclass
class FbChromeEncryptPasswordData:
    password: str
    country_code: str
    user_agent: str
    proxy: Optional[str] = None
