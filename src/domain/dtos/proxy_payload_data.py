from dataclasses import dataclass
from typing import Optional


@dataclass
class ProxyPayloadData:
    proxy_uid: Optional[str] = None
    proxy: Optional[str] = None
    proxy_protocol: Optional[str] = None
    country_code: Optional[str] = None
