from dataclasses import dataclass
from typing import Optional


@dataclass
class EncryptPasswordPayload:
    password: str
    proxy: Optional[str] = None
