import os
import time
import json
from typing import Union, Optional
from requests.exceptions import ProxyError, ConnectionError
from filelock import FileLock, Timeout

from src.common import config
from src.common.logger import logger
from src.domain.dtos.otp_service_response import OTPServiceResponse
from src.application.interfaces.i_otp_service import IOtpService
from src.infrastructure.clients.request_custom import RequestCustom
from src.infrastructure.files.file_reader import FileReader


class CustomContactFileService(IOtpService):
    READ_MAIL_API = 'https://tools.dongvanfb.net'

    def __init__(
        self,
        time_out: int = 60,
        full_mail: str = None,
        **kwargs
    ):
        self.time_out = time_out
        self.full_mail = full_mail
        self.proxy = kwargs.get("proxy", None)

        self.file_reader = FileReader(config.contact_list_dir)
        self.used_file_path = f"{os.path.splitext(config.contact_list_dir)[0]}_used.txt"

    # ============================== #
    #        HELPER FUNCTIONS        #
    # ============================== #

    def _safe_read_and_pop_line(self) -> Optional[str]:
        """
        Đọc 1 dòng đầu tiên trong file `contact_list_dir`, xóa khỏi file,
        và chuyển dòng đó sang file *_used.txt.
        Đảm bảo an toàn khi nhiều luồng cùng truy cập (dùng filelock).
        """
        source_path = config.contact_list_dir
        used_path = self.used_file_path
        lock_path = f"{source_path}.lock"

        if not os.path.exists(source_path):
            logger.error(f"Không tìm thấy file {source_path}")
            return None

        os.makedirs(os.path.dirname(used_path), exist_ok=True)
        lock = FileLock(lock_path, timeout=10)

        try:
            with lock:
                with open(source_path, "r+", encoding="utf-8") as src:
                    lines = src.readlines()
                    if not lines:
                        return None

                    line = lines[0].strip()
                    remaining = lines[1:]

                    # Ghi lại phần còn lại
                    src.seek(0)
                    src.truncate(0)
                    src.writelines(remaining)

                # Ghi dòng đã dùng sang file used
                with open(used_path, "a+", encoding="utf-8") as f:
                    f.write(line + "\n")

                return line

        except Timeout:
            logger.warning("Không thể lock file để đọc contact (timeout).")
            return None
        except Exception as e:
            logger.error(f"Lỗi khi đọc contact: {e}")
            return None

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

            self.proxy = None  # reset proxy nếu lỗi

        return None

    # ============================== #
    #        PUBLIC FUNCTIONS        #
    # ============================== #

    def get_balance(self) -> Union[int, None]:
        return True

    def create(self, temporary_contact: str = None, **kwargs) -> Optional[OTPServiceResponse]:
        """
        Mỗi lần gọi -> lấy 1 contact trong file, chuyển sang *_used.txt và trả về.
        """
        try:
            line = self._safe_read_and_pop_line()
            if not line:
                logger.warning("Không còn contact khả dụng trong file.")
                return None

            line = line.strip()
            contact = line.split('|')[0] if '|' in line else line

            # Nếu dòng chứa email thì dùng email làm contact chính
            if '@' in contact:
                contact_id = line if '|' in line else contact
            else:
                contact_id = contact

            return OTPServiceResponse(
                contact=contact,
                id=contact_id,
                additional_value=line
            )

        except Exception as e:
            logger.warning(f"Failed to create request: {e}")
            return None

    def get_code(self, **kwargs) -> Union[str, None]:
        """
        Gửi request đến API đọc mail để lấy mã xác nhận.
        """
        code = None
        start_time = time.time()

        if not '@' in self.full_mail or '|' not in self.full_mail:
            return None

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

                    with open(log_path, 'a+', encoding='utf-8') as f:
                        f.write(f"Code: {log_message}\n")

                    code = response_code

            except Exception as e:
                logger.error(f'Error while trying to get code: {e}. Retrying...')
            time.sleep(20)

        return code
