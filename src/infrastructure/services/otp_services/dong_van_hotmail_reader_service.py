import os
import time
import json
from typing import Union, Optional
from requests.exceptions import ProxyError, ConnectionError

from src.common import config
from src.common.logger import logger
from src.domain.dtos.otp_service_response import OTPServiceResponse
from src.application.interfaces.i_otp_service import IOtpService
from src.infrastructure.clients.request_custom import RequestCustom
from src.infrastructure.files.file_reader import FileReader


class DongVanHotmailReaderService(IOtpService):
    SERVICE_ID = [1, 2, 3]
    READ_MAIL_API = 'https://tools.dongvanfb.net'

    def __init__(
        self,
        access_token: str,
        api_url: str = 'https://api.dongvanfb.net',
        time_out: int = 60,
        full_mail: str = None,
        **kwargs
    ):
        IOtpService.__init__(self)

        self.access_token = access_token
        self.api_url = api_url
        self.time_out = time_out
        self.full_mail = full_mail
        self.proxy = kwargs.get("proxy", None)

    def _send_request(
        self,
        method: str,
        url: str,
        body: Union[dict, None] = None,
        timeout: Optional[int] = None,
        verify_ssl: bool = True
    ) -> Optional[dict]:
        start_time = time.time()
        while time.time() < start_time + 60:
            try:
                request = RequestCustom(
                    url=url,
                    body=body,
                    proxy=self.proxy,
                    timeout=timeout or self.time_out,
                    verify_ssl=verify_ssl
                )

                response = request.post() if method.lower() == "post" else request.get()

                if response and response.status_code == 200 and response.body:
                    return json.loads(response.body)
            except (ProxyError, ConnectionError) as e:
                logger.error(f"Network error: {e}")
            except Exception as e:
                logger.error(f"Request error: {e}")

            self.proxy = None

        return None

    def get_balance(self) -> Union[int, None]:
        url = f'{self.api_url}/user/balance?apikey={self.access_token}'
        data = self._send_request("get", url)
        return data.get('balance') if data else None

    def create(self, temporary_contact: str = None, **kwargs) -> Optional[OTPServiceResponse]:
        try:
            if temporary_contact:
                contact = temporary_contact.split('|')[0]
                return OTPServiceResponse(id=contact, contact=contact, additional_value=temporary_contact)

            start_time = time.time()
            while time.time() - start_time < self.time_out:
                for service_id in self.SERVICE_ID:
                    url = f'{self.api_url}/user/buy?apikey={self.access_token}&account_type={service_id}&quality=1&type=full'
                    response_data = self._send_request("get", url, verify_ssl=False)
                    if not response_data:
                        continue

                    if 'E_PRODUCT_OUT_STOCK' in str(response_data):
                        continue

                    list_data = response_data.get('data', {}).get('list_data', [])
                    if list_data:
                        first_entry = list_data[0]
                        contact = first_entry.split('|')[0]
                        return OTPServiceResponse(id=contact, contact=contact, additional_value=first_entry)
        except Exception as e:
            logger.warning(f"Failed to create request: {e}")
        return None

    def get_code(self, **kwargs) -> Union[str, None]:
        code = None
        start_time = time.time()

        while not code and time.time() < start_time + self.time_out:
            try:
                parts = self.full_mail.split('|')
                email = parts[0] if len(parts) > 0 else ""
                password = parts[1] if len(parts) > 1 else ""
                refresh_token = parts[2] if len(parts) > 2 else ""
                client_id = parts[3] if len(parts) > 3 else ""

                url = f'{self.READ_MAIL_API}/api/get_code_oauth2'
                payload = {
                    "email": email,
                    "refresh_token": refresh_token,
                    "pass": password,
                    "client_id": client_id,
                    "type": "facebook"
                }

                body_response = self._send_request("post", url, body=payload, verify_ssl=True)

                if body_response and body_response.get('status'):
                    response_time = body_response.get('date')
                    response_code = body_response.get('code')
                    log_message = f"{email}|{response_time}|{response_code}"

                    log_path = os.path.join(config.log_dir, 'log_message.txt')
                    os.makedirs(config.log_dir, exist_ok=True)
                    if not os.path.exists(log_path):
                        open(log_path, 'w', encoding='utf-8').close()

                    logged_lines = FileReader(log_path).read_lines()
                    if not any(log_message in line for line in logged_lines):
                        with open(log_path, 'a+', encoding='utf-8') as f:
                            f.write(f"Code: {log_message}\n")
                        code = response_code
            except Exception as e:
                logger.error(f'Error while trying to get code: {e}. Retrying...')
            time.sleep(20)

        return code
