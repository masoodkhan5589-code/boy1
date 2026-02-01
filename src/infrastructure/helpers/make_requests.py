import time
import requests

from src.application.interfaces.i_make_requests import IMakeRequest
from src.common.logger import logger
from src.infrastructure.clients.request_custom import RequestCustom


class MakeRequest(IMakeRequest):

    def __init__(self, retry_delay_seconds: int = 1, max_retry_attempts: int = 3) -> None:
        self.retry_delay_seconds = retry_delay_seconds
        self.max_retry_attempts = max_retry_attempts
        self.session = requests.Session()

    def _make_request(
            self, method: str, end_point: str, headers: dict = None,
            body: str | dict | bytes = None, files: dict = None, proxy: str = None,
            verify_ssl: bool = True, session: requests.Session = None, timeout: int = 30, allow_redirects: bool = False,
    ) -> any:
        for index in range(1, self.max_retry_attempts + 1):
            try:
                request_args = {
                    "url": end_point,
                    "proxy": proxy,
                    "verify_ssl": verify_ssl,
                    "session": session,
                    "headers": headers,
                    "timeout": timeout,
                    "allow_redirects": allow_redirects
                }

                if method == "POST":
                    if files:
                        request_args["files"] = files

                    if body:
                        request_args["body"] = body

                request = RequestCustom(**request_args)
                response = request.post() if method == "POST" else request.get()
                return response
            except Exception as e:
                error_msg = f"[{index}/{self.max_retry_attempts}] Unexpected error in {method} request to {end_point}: {e}"
                logger.error(error_msg)

            time.sleep(self.retry_delay_seconds)

        return None

    def make_post_request(
            self, end_point: str, headers: dict = None, session: requests.Session = None,
            body: str | dict | bytes = None, files: dict = None,
            proxy: str = None, verify_ssl: bool = True, timeout: int = 30, allow_redirects: bool = False
    ) -> any:
        return self._make_request(
            "POST", end_point, headers,
            body=body, files=files, proxy=proxy,
            verify_ssl=verify_ssl, session=session, timeout=timeout, allow_redirects=allow_redirects
        )

    def make_get_request(
            self, end_point: str, headers: dict = None,
            proxy: str = None, verify_ssl: bool = True,
            session: requests.Session = None, timeout: int = 30, allow_redirects: bool = False
    ) -> any:
        return self._make_request(
            "GET", end_point, headers, proxy=proxy,
            verify_ssl=verify_ssl, session=session, timeout=timeout, allow_redirects=allow_redirects
        )
