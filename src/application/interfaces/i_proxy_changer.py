from abc import ABC, abstractmethod


class IProxyChanger(ABC):

    @abstractmethod
    def change(self) -> bool:
        """Thay đổi cài đặt proxy trên thiết bị."""
        pass

    @abstractmethod
    def enable(self) -> bool:
        """Bật proxy trên thiết bị."""
        pass

    @abstractmethod
    def disable(self) -> bool:
        """Tắt proxy trên thiết bị."""
        pass

    @abstractmethod
    def open_proxy_app(self) -> bool:
        """Mở ứng dụng proxy trên thiết bị (nếu có)."""
        pass
