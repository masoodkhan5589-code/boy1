from abc import ABC, abstractmethod
from typing import Optional, Tuple


class IProxyManager(ABC):
    """Interface cho ProxyManager"""

    @abstractmethod
    def get_proxy(self) -> Optional[Tuple[str, str]]:
        """Lấy 1 proxy chưa dùng (uid, proxy_str).
        Trả về None nếu hết proxy khả dụng."""
        pass

    @abstractmethod
    def release_proxy(self, uid: str) -> None:
        """Giải phóng proxy theo uid để có thể tái sử dụng."""
        pass

    @abstractmethod
    def report_result(self, uid: str, country: str, success: bool) -> None:
        """Ghi nhận kết quả sử dụng proxy:
        - success=True: cộng điểm cho country
        - success=False: trừ điểm cho country
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """Dừng manager, flush dữ liệu ra file."""
        pass

    @abstractmethod
    def get_total(self) -> int:
        """Trả về tổng số proxy load từ file."""
        pass

    @abstractmethod
    def get_in_use_count(self) -> int:
        """Trả về số proxy đang được sử dụng."""
        pass
