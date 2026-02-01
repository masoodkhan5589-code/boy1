from dataclasses import dataclass
from typing import Optional


@dataclass
class AccountAuthResponseData:
    c_user: Optional[str] = None
    access_token: Optional[str] = None
    cookie: Optional[str] = None
