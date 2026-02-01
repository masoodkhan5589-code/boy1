from typing import Optional

from src.application.interfaces.i_contact_manager import IContactManager
from src.common.logger import logger
from src.domain.dtos.otp_service_response import OTPServiceResponse
from src.domain.enums.contact_type import ContactType
from src.domain.enums.opt_service import OtpServices
from src.infrastructure.services.otp_services.custom_contact_file_service import CustomContactFileService
from src.infrastructure.services.otp_services.gmail66_fb_only_service import Gmail66FBOnlyService
from src.infrastructure.services.otp_services.ivasms_service import IVASmsService
from src.infrastructure.services.otp_services.kim_tai_site_service import KimTaiSiteService


class ContactManagement(IContactManager):

    def __init__(
            self,
            otp_service_api_key: str,
            contact_type: str,
            otp_service: str,
            time_out: int = 60,
            **kwargs
    ):
        self.otp_service_api_key = otp_service_api_key
        self.contact_type = contact_type
        self.otp_service = otp_service
        self.time_out = time_out
        self.kwargs = kwargs

        self.service = self._initialize_service()

    def _initialize_service(self):
        """Khởi tạo đúng service một lần duy nhất"""
        if self.contact_type == ContactType.EMAIL.value.key:
            if self.otp_service == OtpServices.GMAIL_66_ONLY_FACEBOOK.value.key:
                return Gmail66FBOnlyService(
                    access_token=self.otp_service_api_key,
                    time_out=self.time_out,
                    proxy=self.kwargs.get('proxy')
                )
            elif self.otp_service == OtpServices.KIMTAI_SITE_EMAIL.value.key:
                return KimTaiSiteService(
                    time_out=self.time_out,
                    proxy=self.kwargs.get('proxy')
                )
            elif self.otp_service == OtpServices.CONTACT_FILE_TXT.value.key:
                return CustomContactFileService()
            elif self.otp_service == OtpServices.IVASMS.value.key:
                return IVASmsService(
                    access_token=self.otp_service_api_key,
                    time_out=self.time_out,
                )

    def get_contact(self, **kwargs) -> Optional[OTPServiceResponse]:
        try:
            if self.contact_type == ContactType.EMAIL.value.key:
                return self.service.create()
        except Exception as e:
            import traceback
            logger.error(f"Error while retrieving contact: {e} - {traceback.format_exc()}")
            return None

    def get_otp(self, otp_service_response: OTPServiceResponse) -> str:
        try:
            if self.contact_type == ContactType.EMAIL.value.key:
                # Cập nhật thông tin nếu cần (ví dụ domain hoặc full_mail)
                if isinstance(self.service, Gmail66FBOnlyService):
                    self.service.order_id = otp_service_response.additional_value
                if isinstance(self.service, CustomContactFileService):
                    self.service.full_mail = otp_service_response.additional_value
                if isinstance(self.service, IVASmsService):
                    self.service.range_number = otp_service_response.additional_value

                return self.service.get_code(email_address=otp_service_response.contact)
            else:
                return self.service.get_code(request_id=otp_service_response.id)
        except Exception as e:
            logger.error(f"Error while retrieving OTP: {e}")
            return ""
