from dataclasses import dataclass
from typing import Optional


@dataclass
class FbLiteLoginPayload:
    id_source: str
    device_id: str
    fb_user_id: str
    fb_password: str
    fb_access_token: Optional[str] = None
    fb_cookie: Optional[str] = None
