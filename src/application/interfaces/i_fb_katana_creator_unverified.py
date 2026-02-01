from abc import ABC, abstractmethod
from typing import Optional, Tuple

from src.application.use_cases.detection_manager_use_case import DetectionManagerUseCase
from src.domain.dtos.fb_creator_data import FbCreatorData


class IFbKatanaCreatorUnverified(ABC):

    @abstractmethod
    def __init__(
            self,
            payload: FbCreatorData,
            detection_manager: DetectionManagerUseCase,
    ):
        pass

    @abstractmethod
    def open_facebook_app(self) -> bool:
        """Mở ứng dụng Facebook và chờ màn hình đăng nhập xuất hiện"""
        pass

    @abstractmethod
    def create_new_account(self) -> bool:
        """Đi tới bước tạo tài khoản mới"""
        pass

    @abstractmethod
    def set_contact(self, contact: str) -> Tuple[bool, bool]:
        """Nhập email hoặc số điện thoại. Trả về (success, try_again)"""
        pass

    @abstractmethod
    def set_full_name(self) -> bool:
        """Nhập họ tên đầy đủ"""
        pass

    @abstractmethod
    def set_dob(self) -> bool:
        """Nhập ngày sinh"""
        pass

    @abstractmethod
    def set_gender(self) -> bool:
        """Chọn giới tính"""
        pass

    @abstractmethod
    def set_password(self) -> bool:
        """Nhập mật khẩu"""
        pass

    @abstractmethod
    def finish_signing_up(self) -> bool:
        """Hoàn tất đăng ký (ấn Sign up, Agree, vv)"""
        pass

    @abstractmethod
    def fetch_account_information(self) -> Tuple[Optional[str], Optional[str], Optional[str], bool]:
        """
        Lấy thông tin tài khoản sau khi đăng ký
        return (facebook_id, cookie, access_token, account_status)
        """
        pass

    @abstractmethod
    def close_facebook_app(self) -> bool:
        """Đóng và clear dữ liệu Facebook app"""
        pass
