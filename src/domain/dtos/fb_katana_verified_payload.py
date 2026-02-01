from dataclasses import dataclass


@dataclass
class FbKatanaVerifiedPayload:
    id_source: str
    fb_user_id: str
    fb_access_token: str
    time_out: int = 90
