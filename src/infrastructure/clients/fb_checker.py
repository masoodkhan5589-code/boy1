import requests

from src.application.interfaces.i_fb_checker import IFbChecker
from src.common.status_constants import StatusConstants
from src.domain.dtos.check_info_token_response_data import CheckInfoTokenResponseData


class FbChecker(IFbChecker):

    @staticmethod
    def check_uid(fb_uid: str) -> bool:
        if not fb_uid:
            return False

        avatar_url = f"https://graph.facebook.com/{fb_uid}/picture?type=normal"
        try:
            response = requests.get(avatar_url, allow_redirects=False, timeout=10)
            if response.status_code == 302:
                redirect_url = response.headers.get("Location", "")
                return "static.xx.fbcdn.net" not in redirect_url
            else:
                return False
        except Exception:
            return True

    def check_token(self, fb_uid: str, fb_access_token: str) -> CheckInfoTokenResponseData:
        result = {"fullname": None, "token_status": True, "account_status": False}
        if not fb_access_token:
            return CheckInfoTokenResponseData(**result)

        # Check live qua UID
        uid_status = self.check_uid(fb_uid)
        result.update({
            "account_status": StatusConstants.ACCOUNT_LIVE if uid_status else StatusConstants.ACCOUNT_DISABLED
        })

        if not uid_status:
            return CheckInfoTokenResponseData(**result)

        # Check live qua token
        graph_api = f"https://graph.facebook.com/me/?access_token={fb_access_token}"

        try:
            response = requests.get(graph_api, allow_redirects=False, timeout=60)
            if response.status_code in [200, 400]:
                data = response.json()

                fb_id = data.get("id")
                fullname = data.get("name")
                error = data.get("error", {})

                if fb_id:  # có id => token hợp lệ, acc đã ver
                    result.update({
                        "fullname": fullname,
                        "token_status": True
                    })
                elif error and error.get("code", 0) == 190 and error.get("error_subcode", 0) == 452:
                    result.update({
                        "token_status": False,
                        "status": StatusConstants.THE_SESSION_HAS_BEEN_INVALIDATED
                    })

        except Exception as e:
            result.update({"status": e})

        return CheckInfoTokenResponseData(**result)
