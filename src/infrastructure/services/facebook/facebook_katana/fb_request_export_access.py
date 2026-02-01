import json
import re
from typing import Optional

from src.application.interfaces.i_fb_request_export_access import IFbRequestExportAccess


class FbRequestExportAccess(IFbRequestExportAccess):
    def export(self, data: str) -> tuple:
        cleaned_data = data.replace('\\', '')

        cookie = self._export_cookies(cleaned_data)
        access_token = self._export_token(cleaned_data)

        if not cookie and not access_token:
            return None, None, None

        match = re.search(r'c_user=(.+?);', cookie)
        if not match:
            return None, None, None

        c_user = match.group(1)
        return c_user, cookie, access_token

    @staticmethod
    def _export_cookies(data: str) -> str:
        match = re.search(r'"session_cookies"\s*:\s*(\[\{.*?\}\])', data)
        if not match:
            return ""

        try:
            cookies_list = json.loads(match.group(1))
            allowed_names = {"xs", "fr", "c_user", "datr"}
            return "; ".join(
                f"{item['name']}={item['value']}"
                for item in cookies_list
                if item.get("name") in allowed_names
            )
        except (json.JSONDecodeError, KeyError):
            return ""

    @staticmethod
    def _export_token(data: str) -> Optional[str]:
        match = re.search(r'"access_token"\s*:\s*"([^"]+)"', data)
        return match.group(1) if match else None
