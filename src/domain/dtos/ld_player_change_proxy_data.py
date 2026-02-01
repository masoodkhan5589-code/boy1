from dataclasses import dataclass
from typing import Optional

from src.domain.dtos.proxy_payload_data import ProxyPayloadData


@dataclass
class LdPlayerChangeProxyData:
    proxy_payload_data: Optional[ProxyPayloadData] = None
    time_out: int = 90
