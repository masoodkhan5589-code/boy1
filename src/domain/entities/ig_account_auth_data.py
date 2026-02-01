import json
import base64
from typing import Optional

from src.common.logger import logger


class IgAccountAuthData:
    mid: Optional[str] = None
    x_mid: Optional[str] = None
    ds_user_id: Optional[str] = None
    authorization: Optional[str] = None
    ig_u_ds_user_id: Optional[str] = None
    ig_u_rur: Optional[str] = None

    def __init__(self, mid=None, x_mid=None, ds_user_id=None, authorization=None, ig_u_ds_user_id=None, ig_u_rur=None):
        self.mid = mid
        self.x_mid = x_mid
        self.ds_user_id = ds_user_id
        self.authorization = authorization
        self.ig_u_ds_user_id = ig_u_ds_user_id
        self.ig_u_rur = ig_u_rur

    def parse_authorization(self) -> dict:
        """Decode the authorization token and return the resulting dictionary."""
        if self.authorization and "Bearer IGT:2:" in self.authorization:
            base64_token = self.authorization.split("Bearer IGT:2:")[-1]
            try:
                decoded_data = base64.b64decode(base64_token).decode("utf-8")
                return json.loads(decoded_data)
            except Exception as e:
                raise ValueError(f"Failed to decode authorization token: {e}")
        return {}

    def to_cookie(self) -> Optional[str]:
        """Create a cookie string from the data."""
        # Parse authorization to extract additional fields
        auth_data = self.parse_authorization()

        # Extract ds_user_id and sessionid from decoded authorization data
        ds_user_id = auth_data.get("ds_user_id", self.ds_user_id)
        sessionid = auth_data.get("sessionid", None)

        # Ensure all required fields are present
        if not (ds_user_id and sessionid and self.mid and self.ig_u_rur):
            logger.error("Missing required fields to create the cookie.")
            return None

        # Build the cookie string
        cookie_string = (
            f"ds_user_id={ds_user_id}; "
            f"sessionid={sessionid}; "
            f"mid={self.mid}; "
            f"rur={str(self.ig_u_rur).replace(',', '\\')}"
        )
        return cookie_string
