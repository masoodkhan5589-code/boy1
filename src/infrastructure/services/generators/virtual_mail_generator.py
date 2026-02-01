import random
import string

from src.common.utils import generate_username
from src.domain.dtos.otp_service_response import OTPServiceResponse


class VirtualMailGenerator:
    def __init__(self, domains=None):
        if domains is None:
            self.domains = ["gmail.com", "hotmail.com", "yahoo.com"]
        else:
            self.domains = domains

    @staticmethod
    def _generate_random_name(length=6):
        # Tạo một chuỗi ngẫu nhiên gồm chữ cái thường
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def create(self, first_name: str = None, last_name: str = None) -> OTPServiceResponse:
        # Nếu không có tên, tự tạo tên ngẫu nhiên
        if not first_name:
            first_name = self._generate_random_name(random.randint(3, 6))
        if not last_name:
            last_name = self._generate_random_name(random.randint(3, 6))

        username = generate_username(first_name=first_name, last_name=last_name)
        domain = random.choice(self.domains)

        new_contact = f"{username}@{domain}"

        return OTPServiceResponse(id=new_contact, contact=new_contact, additional_value=new_contact)

    @staticmethod
    def get_code() -> None:
        return None
