import brotli
import gzip
import zlib
import urllib3
import requests
from argparse import Namespace

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RequestCustom:

    def __init__(
            self,
            url,
            headers=None,
            body=None,
            proxy=None,
            files=None,
            allow_redirects=True,
            session=None,
            timeout=30,
            verify_ssl=True
    ):
        self.url = url
        self.body = body
        self.proxy = proxy
        self.files = files
        self.allow_redirects = allow_redirects
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = session or requests.Session()
        self.headers = headers or {}

    def get(self):
        return self._send_request(method='GET')

    def post(self):
        return self._send_request(method='POST')

    def _send_request(self, method='GET'):
        result = {
            'cookie': '',
            'response_header': '',
            'request_header': '',
            'session': '',
            'body': '',
            'status': False,
            'status_code': '',
        }

        try:
            req = requests.Request(
                method,
                self.url,
                headers=self.headers,
                data=self.body,
                files=self.files if method == 'POST' else None
            )
            prepared_req = self.session.prepare_request(req)

            response = self.session.send(
                prepared_req,
                proxies=self.map_proxy(),
                allow_redirects=self.allow_redirects,
                timeout=self.timeout,
                verify=self.verify_ssl
            )

            response_body = self._decode_response(response)
            result.update({
                'cookie': self.session.cookies.get_dict(),
                'response_header': dict(response.headers),
                'request_header': dict(prepared_req.headers),
                'session': self.session,
                'body': response_body,
                'status': True,
                'status_code': response.status_code,
            })

        except Exception as e:
            raise Exception(f"Request Error: {e}")

        return Namespace(**result)

    def map_proxy(self):
        """
        Hỗ trợ:
          - ip:port
          - ip:port:user:pass (mặc định SOCKS5)
          - user:pass@ip:port
          - socks5://ip:port hoặc http://ip:port
        """
        if not self.proxy or str(self.proxy).strip().lower() == "none":
            return None

        proxy = str(self.proxy).strip()

        # Nếu đã có prefix
        if proxy.startswith(("http://", "https://", "socks5://")):
            proto = proxy.split("://")[0]
            clean_proxy = proxy.split("://", 1)[1]
        else:
            proto = "http"
            clean_proxy = proxy

        # Dạng ip:port:user:pass → đổi định dạng sang user:pass@ip:port
        if clean_proxy.count(":") == 3:
            ip, port, user, pwd = clean_proxy.split(":")
            clean_proxy = f"{user}:{pwd}@{ip}:{port}"

        # Dạng user:pass@ip:port → giữ nguyên
        elif "@" in clean_proxy:
            pass

        return {
            "http": f"{proto}://{clean_proxy}",
            "https": f"{proto}://{clean_proxy}",
        }

    @staticmethod
    def _decode_response(response):
        encoding = response.headers.get('Content-Encoding', '').lower()
        raw_content = response.content
        try:
            # Nếu là JSON (không cần giải nén)
            if raw_content.startswith(b'{') or raw_content.startswith(b'['):
                return raw_content.decode('utf-8', errors='replace')

            # Giải nén dựa trên Content-Encoding
            if 'br' in encoding:
                return brotli.decompress(raw_content).decode('utf-8', errors='replace')
            elif 'gzip' in encoding:
                return gzip.decompress(raw_content).decode('utf-8', errors='replace')
            elif 'deflate' in encoding:
                return zlib.decompress(raw_content).decode('utf-8', errors='replace')
            else:
                return raw_content.decode('utf-8', errors='replace')

        except Exception:
            return raw_content.decode('utf-8', errors='replace')
