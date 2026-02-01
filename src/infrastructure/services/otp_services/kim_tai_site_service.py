import os
import random
import re
import string
import time
from typing import Union, Optional
from requests.exceptions import ProxyError, ConnectionError

from src.common import config
from src.common.logger import logger
from src.domain.dtos.otp_service_response import OTPServiceResponse
from src.application.interfaces.i_otp_service import IOtpService
from src.infrastructure.clients.request_custom import RequestCustom
from src.infrastructure.files.file_writer import FileWriter


class KimTaiSiteService(IOtpService):

    def __init__(
        self,
        api_url: str = 'https://kimtai.site',
        time_out: int = 60,
        **kwargs
    ):
        self.api_url = api_url
        self.time_out = time_out
        self.proxy = kwargs.get("proxy", None)

    def _send_request(
        self,
        method: str,
        url: str,
        body: Union[dict, None] = None,
        timeout: Optional[int] = None,
        verify_ssl: bool = True
    ) -> Optional[RequestCustom]:
        start_time = time.time()
        while time.time() < start_time + 60:
            try:

                request = RequestCustom(
                    url=url,
                    body=body,
                    timeout=timeout or self.time_out,
                    verify_ssl=verify_ssl
                )

                response = request.post() if method.lower() == "post" else request.get()
                if response and response.status_code in [200] and response.body:
                    return response.body
            except (ProxyError, ConnectionError) as e:
                logger.error(f"Network error: {e}")
            except Exception as e:
                logger.error(f"Request error: {e}")

        return None

    def get_balance(self) -> Union[int, None]:
        return None

    def create(self, max_attempts: int = 5, **kwargs) -> Optional[OTPServiceResponse]:
        domain_site = ['stotp.site', 'stmail.site', 'thienthanh.site', 'kimtai.site']
        username = self._generate_random_name()

        contact = f'{username}@{random.choice(domain_site)}'
        return OTPServiceResponse(
            contact=contact,
            id=contact,
            additional_value=contact
        )

    def get_code(self, **kwargs) -> Union[str, None]:
        code = None
        start_time = time.time()
        email = kwargs.get("email_address", "")

        if not email:
            return None

        while not code and time.time() < start_time + self.time_out:
            try:
                url = f'{self.api_url}/?email={email}'
                body_response = self._send_request("get", url, verify_ssl=False)
                if not body_response:
                    continue

                condition = 'facebook'
                if body_response and condition in str(body_response).lower():
                    if otp_code := self._extract_otp(str(body_response)):
                        self._log_message(email, str(otp_code))
                        code = otp_code

            except (ProxyError, ConnectionError) as e:
                logger.error(f"Network error: {e}")
            except Exception as e:
                logger.error(f'Error while getting OTP code: {e}. Retrying...')

            time.sleep(1)

        return code

    @staticmethod
    def _generate_random_name(length=6):
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    @staticmethod
    def _log_message(email: str, code: str):
        file_writer = FileWriter(os.path.join(config.log_dir, 'log_message.txt'))
        file_writer.append(f"Mail: {email} Code: {code}\n")

    @staticmethod
    def _extract_otp(content: str):
        if match := re.search(r'FB-(\d{5,8})', content):
            return match.group(1).replace(" ", "")

        pattern = r'<div[^>]*class=["\']mail-subject["\'][^>]*>.*?(\d{4,8}).*?</div>'
        if match := re.search(pattern, content, re.DOTALL):
            return match.group(1).replace(" ", "")

        return None
