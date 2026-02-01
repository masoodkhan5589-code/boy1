from abc import ABC, abstractmethod
from typing import Optional, Tuple

from src.application.interfaces.i_detection_manager import IDetectionManager
from src.domain.dtos.fb_katana_verify_account_data import FbKatanaVerifyAccountData


class IFbKatanaVerify(ABC):
    """
    Interface cho lớp hỗ trợ xác minh tài khoản Facebook thông qua Facebook Katana.
    """

    @abstractmethod
    def __init__(
            self,
            payload: FbKatanaVerifyAccountData,
            detection_manager: IDetectionManager,
    ):
        pass

    @abstractmethod
    def confirm_by_mobile_number(self, phone_number: str) -> tuple[bool, bool]:
        """
        Mở trang thay đổi thông tin liên hệ của tài khoản.

        :return: True nếu chuyển đến màn hình thay đổi liên hệ thành công, ngược lại là False.
        """
        pass

    @abstractmethod
    def confirm_by_email(self, primary_email: str) -> tuple[bool, bool]:
        """
        Mở trang thay đổi thông tin liên hệ của tài khoản.

        :return: True nếu chuyển đến màn hình thay đổi liên hệ thành công, ngược lại là False.
        """
        pass

    @abstractmethod
    def confirmation_code(self, confirmation_code: str | int) -> bool:
        """
        Nhập mã xác nhận (OTP) để xác minh tài khoản.

        :param confirmation_code: Mã xác nhận.
        :return: True nếu xác nhận thành công, ngược lại là False.
        """
        pass

    @abstractmethod
    def skip_setup_account(self) -> bool:
        """
        Bỏ qua các bước thiết lập tài khoản ban đầu sau khi đăng nhập/xác minh.

        :return: True nếu thành công, ngược lại là False.
        """
        pass

    @abstractmethod
    def fetch_account_information(self) -> Tuple[Optional[str], Optional[str], Optional[str], bool]:
        """
        Lấy thông tin truy cập của tài khoản (ID, cookie, access token).

        :return: Tuple chứa facebook_id, cookie, access_token và account_status.
        """
        pass

    @abstractmethod
    def close_facebook_app(self) -> bool:
        """
        Thực hiện đóng và xóa dữ liệu ứng dụng Facebook.

        :return: True nếu thành công, ngược lại là False.
        """
        pass

    @property
    @abstractmethod
    def payload(self) -> FbKatanaVerifyAccountData:
        """
        Dữ liệu đầu vào của quá trình xác minh tài khoản.
        """
        pass
