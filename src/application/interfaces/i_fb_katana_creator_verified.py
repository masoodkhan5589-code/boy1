from abc import ABC, abstractmethod
from typing import Optional, Tuple

from src.application.use_cases.detection_manager_use_case import DetectionManagerUseCase
from src.domain.dtos.fb_creator_data import FbCreatorData


class IFbKatanaCreatorVerified(ABC):

    @abstractmethod
    def __init__(
            self,
            payload: FbCreatorData,
            detection_manager: DetectionManagerUseCase,
    ):
        pass

    @abstractmethod
    def open_facebook_app(self) -> bool:
        """
        Mở ứng dụng Facebook và chờ màn hình đăng nhập.
        """
        pass

    @abstractmethod
    def create_new_account(self) -> bool:
        """
        Bắt đầu quy trình tạo tài khoản mới.
        """
        pass

    @abstractmethod
    def set_full_name(self) -> bool:
        """
        Điền tên và họ.
        """
        pass

    @abstractmethod
    def set_dob(self) -> bool:
        """
        Thiết lập ngày tháng năm sinh.
        """
        pass

    @abstractmethod
    def set_gender(self) -> bool:
        """
        Chọn giới tính.
        """
        pass

    @abstractmethod
    def set_contact(self, contact: str) -> tuple[bool, bool]:
        """
        Điền thông tin liên hệ (email/số điện thoại).
        """
        pass

    @abstractmethod
    def set_password(self) -> bool:
        """
        Tạo và điền mật khẩu.
        """
        pass

    @abstractmethod
    def finish_signing_up(self) -> bool:
        """
        Hoàn thành bước đăng ký cuối cùng.
        """
        pass

    @abstractmethod
    def confirm_by_email(self, primary_email: str) -> Tuple[bool, bool]:
        """
        Xác nhận tài khoản qua email.
        """
        pass

    @abstractmethod
    def confirm_by_mobile_number(self, phone_number: str) -> tuple[bool, bool]:
        pass

    @abstractmethod
    def confirmation_code(self, confirmation_code: str | int) -> bool:
        """
        Nhập mã xác nhận.
        """
        pass

    @abstractmethod
    def skip_setup_account(self) -> bool:
        """
        Bỏ qua các bước thiết lập tài khoản ban đầu.
        """
        pass

    @abstractmethod
    def fetch_account_information(self) -> Tuple[Optional[str], Optional[str], Optional[str], bool]:
        """
        Lấy thông tin tài khoản sau khi đăng ký thành công.
        """
        pass

    @abstractmethod
    def close_facebook_app(self) -> bool:
        """
        Đóng và dọn dẹp dữ liệu ứng dụng.
        """
        pass
