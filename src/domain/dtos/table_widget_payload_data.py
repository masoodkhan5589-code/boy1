from dataclasses import dataclass
from typing import Optional


@dataclass
class TableWidgetPayloadData:
    id_source: str
    uid: Optional[str] = None
    password: Optional[str] = None
    twofactor: Optional[str] = None
    cookie: Optional[str] = None
    bearer_token: Optional[str] = None
    fullname: Optional[str] = None
    contact: Optional[str] = None
    otp: Optional[str] = None
    create_date: Optional[str] = None
    proxy: Optional[str] = None
    ip_address: Optional[str] = None
    device: Optional[str] = None
    is_verified: Optional[str] = None
    account_status: Optional[str] = None
    total_time: Optional[str] = None
    status: Optional[str] = None
