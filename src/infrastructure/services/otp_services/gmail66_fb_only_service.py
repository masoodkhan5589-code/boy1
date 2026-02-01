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


class Gmail66FBOnlyService(IOtpService):

    def __init__(
        self,
        access_token: str,
        api_url: str = 'http://gmail66.shop/api/v1',
        time_out: int = 60,
        **kwargs
    ):
        IOtpService.__init__(self)

        self.access_token = access_token
        self.api_url = api_url
        self.time_out = time_out
        self.proxy = kwargs.get("proxy", None)
        self.order_id = kwargs.get("order_id", None)

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
                    timeout=timeout or self.time_out,
                    verify_ssl=verify_ssl
                )

                response = request.post() if method.lower() == "post" else request.get()
                if response and response.status_code in [200, 400] and response.body:
                    return json.loads(response.body)
            except (ProxyError, ConnectionError) as e:
                logger.error(f"Network error: {e}")
            except Exception as e:
                logger.error(f"Request error: {e}")

        return None

    def get_balance(self) -> Union[int, None]:
        return None

    def create(self, max_attempts: int = 5, **kwargs) -> Optional[OTPServiceResponse]:
        try:
            url = f'{self.api_url}/rent-mail?api_key={self.access_token}&service=facebook'
            response_data = self._send_request("get", url, verify_ssl=False)

            if response_data and response_data.get("success"):
                order_id = response_data.get("order_id")
                contact = response_data.get("mail")
                return OTPServiceResponse(id=contact, contact=contact, additional_value=order_id)

        except Exception as e:
            logger.warning(f"Failed to create request: {e}")
        return None

    def get_code(self, **kwargs) -> Union[str, None]:
        code = None
        start_time = time.time()

        if not self.order_id:
            return None

        while not code and time.time() < start_time + self.time_out:
            try:
                url = f'{self.api_url}/check-otp/{self.order_id}?api_key={self.access_token}'
                body_response = self._send_request("get", url, verify_ssl=True)

                response_status = body_response.get('success')
                response_code = body_response.get('otp', None)
                if body_response and response_status and response_code:
                    log_message = f"{kwargs.get("email_address")}|{response_code}"

                    log_path = os.path.join(config.log_dir, 'log_message.txt')
                    os.makedirs(config.log_dir, exist_ok=True)
                    if not os.path.exists(log_path):
                        open(log_path, 'w', encoding='utf-8').close()

                    logged_lines = FileReader(log_path).read_lines()
                    if not any(log_message in line for line in logged_lines):
                        with open(log_path, 'a+', encoding='utf-8') as f:
                            f.write(f"{log_message}\n")
                        code = response_code
            except Exception as e:
                logger.error(f'Error while trying to get code: {e}. Retrying...')
            time.sleep(5)

        return code
