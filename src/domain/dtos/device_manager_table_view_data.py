from dataclasses import dataclass
from typing import Optional


@dataclass
class DeviceManagerTableViewData:
    id_source: str
    device_serial: Optional[str] = None
    version: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    sdk: Optional[str] = None
    mac: Optional[str] = None
    status: Optional[str] = None
