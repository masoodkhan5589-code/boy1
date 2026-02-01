from dataclasses import dataclass
from typing import Optional


@dataclass
class FbKatanaLoginPayload:
    id_source: str
    fb_user_id: str
    fb_password: str
    fb_two_factor: Optional[str] = None
    time_out: int = 90
