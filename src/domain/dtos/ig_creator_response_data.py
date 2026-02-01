from typing import Optional
from dataclasses import dataclass


@dataclass
class IGCreatorResponseData:
    username: Optional[str] = None
    password: Optional[str] = None
    twofactor: Optional[str] = None
    cookie: Optional[str] = None
    bearer_token: Optional[str] = None
    fullname: Optional[str] = None
    contact: Optional[str] = None
    otp: Optional[str] = None
    proxy: Optional[str] = None
    ip_address: Optional[str] = None
    create_date: Optional[str] = None
    device: Optional[str] = None
    account_status: Optional[str] = None
    status: Optional[str] = None
