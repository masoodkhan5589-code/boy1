from dataclasses import dataclass
from typing import Optional


@dataclass
class CheckInfoTokenResponseData:
    fullname: Optional[str] = None
    token_status: Optional[str] = None
    account_status: Optional[bool] = False
    status: Optional[str] = None
