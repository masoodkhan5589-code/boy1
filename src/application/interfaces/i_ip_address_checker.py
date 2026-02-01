from abc import ABC, abstractmethod


class IIPAddressChecker(ABC):
    def __init__(self):
        self.country_code = None

    @abstractmethod
    def get_current_ip(self, proxy: str = None, time_out: int = 10):
        pass

    @abstractmethod
    def get_current_country_code(self) -> str:
        pass
