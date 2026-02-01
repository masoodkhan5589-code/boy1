from dataclasses import dataclass
from typing import Optional


@dataclass
class FacebookAuthenticatorPayload:
    device_id: str
    secure_family_device_id: str
    family_device_id: str
    waterfall_id: str
    machine_id: str
    bloks_version: str
    facebook_user: str
    facebook_password: str
    two_factor_key: str
    proxy: Optional[str] = None
