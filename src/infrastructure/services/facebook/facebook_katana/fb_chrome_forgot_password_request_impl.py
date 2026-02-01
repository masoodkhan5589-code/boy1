import json
import random
import re
from typing import Tuple, Optional, Dict
from urllib.parse import urlencode

import requests

from src.application.interfaces.i_fb_chrome_forgot_password_request import IFbChromeForgotPasswordRequest
from src.common.logger import logger
from src.common.status_constants import StatusConstants
from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData
from src.infrastructure.services.facebook.facebook_katana.fb_katana_verified_tut_base import \
    FbKatanaVerifiedTutBase


class FbChromeForgotPasswordRequestImpl(FbKatanaVerifiedTutBase, IFbChromeForgotPasswordRequest):

    HTTP_ENDPOINT = "https://www.facebook.com"

    def __init__(self, virtual_device_info_data: VirtualDeviceInfoData, proxy_payload: ProxyPayloadData):
        super().__init__(virtual_device_info_data, proxy_payload)

        self.status = StatusConstants()
        self.redirected_url: Optional[str] = None
        self.recover_method: Optional[str] = None
        self.lsd: Optional[str] = None
        self.cuid: Optional[str] = None

    def get_facebook_page(self, session: requests.Session) -> Tuple[bool, requests.Session]:
        headers = self._build_get_headers()
        request = self.make_request.make_get_request(
            end_point=f"{self.HTTP_ENDPOINT}/login/identify/?ctx=recover&ars=facebook_login&from_login_screen=0",
            headers=headers,
            proxy=self.proxy_payload.proxy,
            session=session
        )

        if request and request.status_code == 200:
            session = request.session
            match_lsd = re.search('lsd" value="(.+?)"', request.body)

            if match_lsd and match_lsd.group(1):
                self.lsd = match_lsd.group(1)
            return True, session

        return False, session

    def recover(self, contact: str, session: requests.Session) -> Tuple[bool, requests.Session]:
        payload = {
            "jazoest": random.randrange(1111, 9999),
            "lsd": self.lsd,
            "email": str(contact),
            "did_submit": "1",
            "__user": "0",
            "__a": "1",
            "__req": "5",
            "__hs": "20396.BP:DEFAULT.2.0...0",
            "dpr": "2",
            "__ccg": "GOOD",
            "__rev": "1029358589",
            "__s": "nrle6r:rcu8ps:pw3chg",
            "__hsi": "7568790158287978199",
            "__dyn": "7xeUmwkHg7ebwKBAg5S1Dxu13wqovzEdEc8uxa0CEbo1nEhw2nVE4W0qa0FE2awt81s8hwGwQw4iwBgao6C0Mo2swaO4U2zxe3C0D85a1qw8Xxm16wa-0raazo11E2ZwrU6C0hq1Iw6PG2O1TwmU3ywo81V8",
            "__hsdp": None,
            "__hblp": None,
            "__spin_r": "1029358589",
            "__spin_b": "trunk",
            "__spin_t": "1762246284"
        }
        headers = self._build_post_headers()

        request = self.make_request.make_post_request(
            end_point=f"{self.HTTP_ENDPOINT}/ajax/login/help/identify.php?ctx=recover",
            headers=headers,
            body=urlencode(payload),
            proxy=self.proxy_payload.proxy,
            session=session
        )

        if request and request.status_code == 200 and 'redirectPageTo' in request.body:
            session = request.session
            self.redirected_url = self._extract_redirect_url(request.body)
            return True, session

        return False, session

    def get_redirect_page(self, session: requests.Session) -> Tuple[bool, requests.Session]:
        headers = self._build_get_headers()
        request = self.make_request.make_get_request(
            end_point=f"{self.HTTP_ENDPOINT}{self.redirected_url}",
            headers=headers,
            proxy=self.proxy_payload.proxy,
            session=session
        )

        if request and request.status_code == 200 and 'send_sms' in request.body:
            session = request.session
            match_method = re.search('send_sms:(.+?)"', request.body)
            match_lsd = re.search('lsd" value="(.+?)"', request.body)

            if match_method and match_method.group(1):
                self.recover_method = f"send_sms:{match_method.group(1)}"

            if match_lsd and match_lsd.group(1):
                self.lsd = match_lsd.group(1)

            return True, session
        return False, session

    def send_recovery_request(self, session: requests.Session) -> Tuple[bool, Optional[str], requests.Session]:
        if not self.recover_method or not self.lsd:
            return False, self.status.NO_METHOD_FOR_SEND_SMS, session

        headers = self._build_post_headers()
        payload = {
            "jazoest": str(random.randrange(1111, 9999)),
            "lsd": self.lsd,
            "openid_provider_id": "",
            "openid_provider_name": "",
            "recover_method": self.recover_method,
            "reset_action": "1",
            "__aaid": "0",
            "__user": "0",
            "__a": "1",
            "__req": "8",
            "__hs": "20396.BP:DEFAULT.2.0...0",
            "dpr": "2",
            "__ccg": "GOOD",
            "__rev": "1029358589",
            "__s": "nrle6r:rcu8ps:3j4kbv",
            "__hsi": "7568790206048015703",
            "__dyn": "7xeUmwkHgmwn8yEbFp41twWwIxu13wqovzEdEc8uxa0z8S2Sawba1DwUx60GE1J9E4W0qa321Rw8G11wBz81s8hwGwQw4iwBgao6C0Mo2swaOfK0zEkxe3C0D85a1qwuEjUlwhEe87q7U1oEbUGdw45g2cwMwrUK1twmk0KU6O1FwlU7S12DzUoG2OU6G8wLwHwGwbu1wweWawwwOwgo5i",
            "__hsdp": "gIMX6Mk8Gqh2Yc1nKghoyaAGBUxLUAObhanKaxvGV8RedBh2J0nhrg4lADwXAafz8iyoAOgdU98pAgzdlie8UgEGJA8ICRhFEK2Bx6t5A132sdMH1tgN0QjhE2Vw",
            "__hblp": "0Vwbu222i0qC6E2Hw8W2C1qwoE7i0bOw6Ow3fo3Aw1dK0Oo0KK0dzw51w3381fU762Gew50wgo1j8sw-xWu6Eco9E2Tws8jwMwj8158fo29wVwvE4e0iu0bWwnE-1Uw4zw41w9m15waGfwgo6q0iu1Qw9aE7i1qxq2-0GloG3m4UhFADG8gaUhx60w8dE6q8wxwFwnUdVQ0hu0bPwhE4-585u4O0_xm6U2axy8wDwpojwCzrwlE2ywdC4UgxVx20gi262uewb6",
            "__spin_r": "1029358589",
            "__spin_b": "trunk",
            "__spin_t": "1762246295"
        }

        request = self.make_request.make_post_request(
            end_point=f"{self.HTTP_ENDPOINT}/ajax/recover/initiate/?lara=0",
            headers=headers,
            body=urlencode(payload),
            proxy=self.proxy_payload.proxy,
            session=session
        )

        if not request or not request.status_code == 200 or not hasattr(request, "body"):
            return False, self.status.RECOVERY_FAILED, session

        session = request.session
        body_str = str(request.body).replace("\\", "")

        if 'recover/code' in body_str and "cuid" in body_str:
            cuid_match = re.search('cuid=(.+?)&', body_str)
            if cuid_match:
                self.cuid = cuid_match.group(1)
                return True, self.status.VERIFICATION_SENT_VIA_SMS_SUCCESSFULLY, session

        return False, self.status.FAILED_TO_VERIFICATION_SENT_VIA_SMS, session

    def confirmation_code_request(self, session: requests.Session, phone_number: str, confirmation_code: str) -> Tuple[bool, requests.Session]:
        if not self.lsd or not self.cuid:
            return False, session

        headers = self._build_post_headers()
        payload = {
            "jazoest": str(random.randrange(1111, 9999)),
            "lsd": self.lsd,
            "n": confirmation_code,
            "reset_action": "1",
        }

        request = self.make_request.make_post_request(
            end_point=f"{self.HTTP_ENDPOINT}/recover/code/?ph[0]={phone_number}&rm=send_sms&spc=0&cuid={self.cuid}&fl=default_recover&wsr=0",
            headers=headers,
            body=urlencode(payload),
            proxy=self.proxy_payload.proxy,
            session=session
        )

        if request and request.status_code == 200 and 'code' in request.body:
            session = request.session
            return True, session

        return False, session

    @staticmethod
    def _extract_redirect_url(response_text: str) -> str | None:
        clean_text = re.sub(r"^for\s*\(.*?\);", "", response_text).strip()

        try:
            data = json.loads(clean_text)
            jsmods = data.get("jsmods", {})
            requires = jsmods.get("require", [])
            for req in requires:
                if req and isinstance(req, list):
                    if req[0] == "ServerRedirect" and isinstance(req[-1], list):
                        redirect_info = req[-1]
                        if redirect_info and isinstance(redirect_info[0], str):
                            return redirect_info[0]
        except Exception as e:
            logger.error(f"Error while extracting redirect_url: {e}")

        return None

    @staticmethod
    def _build_get_headers() -> Dict:
        return {
            "Dpr": "1",
            "Viewport-Width": "1200",
            "Sec-Ch-Ua": '"Chromium";v="141", "Not?A_Brand";v="8"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Sec-Ch-Ua-Platform-Version": "",
            "Sec-Ch-Ua-Model": "",
            "Sec-Ch-Ua-Full-Version-List": "",
            "Sec-Ch-Prefers-Color-Scheme": "dark",
            "Accept-Language": "en-US,en;q=0.9",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Accept-Encoding": "gzip, deflate, br",
            "Priority": "u=0, i",
            "Connection": "keep-alive"
        }

    def _build_post_headers(self) -> Dict:
        return {
            "Host": "www.facebook.com",
            "Sec-Ch-Ua-Platform": "\"macOS\"",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": "\"Chromium\";v=\"141\", \"Not?A_Brand\";v=\"8\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "X-Asbd-Id": "359341",
            "X-Fb-Lsd": self.lsd,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "Origin": "https://www.facebook.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Encoding": "gzip, deflate, br",
            "Priority": "u=1, i"
        }
