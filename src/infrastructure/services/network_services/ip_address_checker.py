import json
from src.application.interfaces.i_ip_address_checker import IIPAddressChecker
from src.infrastructure.clients.request_custom import RequestCustom


class IPAddressChecker(IIPAddressChecker):
    def __init__(self):
        super().__init__()
        self.country_code = None

    @staticmethod
    def _fetch_ip_info(url: str, proxy: str, timeout: int):
        """Helper để fetch IP info từ API"""
        try:
            request = RequestCustom(
                url=url, proxy=proxy, timeout=timeout, verify_ssl=False
            ).get()
            return json.loads(request.body)
        except Exception:
            return None

    def get_current_ip(self, proxy: str = None, time_out: int = 10):
        # Danh sách API fallback
        apis = [
            ("https://api.myip.com/", "ip", "cc"),
            ("https://ipinfo.io/json", "ip", "country"),
        ]

        for url, ip_key, cc_key in apis:
            response = self._fetch_ip_info(url, proxy, time_out)
            if response and ip_key in response and cc_key in response:
                ip_address = response.get(ip_key, "Unable to determine IP.")
                self.country_code = response.get(cc_key, None)
                return f"{self.country_code} - {ip_address}"

        return None

    def get_current_country_code(self) -> str:
        return self.country_code
