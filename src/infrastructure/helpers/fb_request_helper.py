from typing import Dict, Any

from src.application.interfaces.i_fb_app_helper import IFbAppHelper
from src.common.status_constants import StatusConstants
from src.domain.dtos.otp_service_response import OTPServiceResponse
from src.domain.dtos.setting_loader_data import SettingLoaderData
from src.infrastructure.clients.fb_checker import FbChecker
from src.infrastructure.helpers.base_app_helper import BaseAppHelper
from src.infrastructure.contact_management import ContactManagement
from src.infrastructure.services.proxy_services.proxy_manager import ProxyManager


class FbRequestHelper(BaseAppHelper, IFbAppHelper):
    def __init__(
            self,
            id_source: str,
            proxies_manager: ProxyManager,
            status_manager: StatusConstants,
            settings: SettingLoaderData,
            execute_tasks: callable,
            response_to_table_widget: callable,
    ):
        result = {
            'uid': "", 'password': "", 'twofactor': "", 'cookie': "",
            'bearer_token': "", 'fullname': '', 'contact': "", 'proxy': "", 'ip_address': "",
            'create_date': "", 'device': "", 'is_verified': "",
            'account_status': "", 'status': "",
        }
        super().__init__(
            id_source=id_source,
            result=result,
            settings=settings,
            table_data_type="facebook",
            response_to_table_widget=response_to_table_widget
        )

        self._proxies_manager = proxies_manager
        self._status_manager = status_manager
        self._execute_tasks = execute_tasks

        self._fb_checker = FbChecker()
        self._error = False
        self._verified = False
        self._unverified = True
        self._try_again = False
        self._account_disabled = False
        self.add_contact_error = False
        self.change_contact_error = False

    def check_live_account(self, check_info_token: bool = False) -> bool:
        facebook_id = self._result.get("uid")
        access_token = self._result.get("bearer_token")

        # Không check token hoặc có token → chỉ check UID
        if not check_info_token or not (facebook_id and access_token):
            is_live = self._fb_checker.check_uid(facebook_id)
            account_status = (
                self._status_manager.ACCOUNT_LIVE if is_live else self._status_manager.ACCOUNT_DISABLED
            )
            self.account_disabled = not is_live
            return self.update_status(
                account_status=account_status,
                status=account_status,
                success=is_live,
            )

        # Có token → check chi tiết
        resp = self._fb_checker.check_token(facebook_id, access_token)

        is_live = resp.account_status == self._status_manager.ACCOUNT_LIVE
        self.account_disabled = not is_live

        verified_status = (
            self._status_manager.VERIFIED
            if self.verified and resp.token_status
            else self._status_manager.UNVERIFIED
            if resp.token_status
            else self._status_manager.UNKNOWN
        )

        return self.update_status(
            fullname=resp.fullname,
            is_verified=verified_status,
            account_status=resp.account_status,
            status=resp.status,
            success=is_live,
        )

    # === Properties & Setters ===
    @property
    def id_source(self) -> str:
        return self._id_source

    @property
    def proxies_manager_instance(self) -> ProxyManager:
        return self._proxies_manager

    @property
    def status_manager_instance(self) -> StatusConstants:
        return self._status_manager

    @property
    def primary_contact_management(self) -> ContactManagement:
        return self._primary_contact

    @property
    def secondary_contact_management(self) -> ContactManagement:
        return self._secondary_contact

    @property
    def primary_otp_service_response(self) -> OTPServiceResponse:
        return self._primary_otp_response

    @primary_otp_service_response.setter
    def primary_otp_service_response(self, value: OTPServiceResponse):
        self._primary_otp_response = value

    @property
    def secondary_otp_service_response(self) -> OTPServiceResponse:
        return self._secondary_otp_response

    @secondary_otp_service_response.setter
    def secondary_otp_service_response(self, value: OTPServiceResponse):
        self._secondary_otp_response = value

    @property
    def result(self) -> Dict[str, Any]:
        return self._result

    @result.setter
    def result(self, value: Dict[str, Any]):
        self._result = value

    @property
    def verified(self) -> bool:
        return self._verified

    @verified.setter
    def verified(self, value: bool):
        self._verified = value

    @property
    def unverified(self) -> bool:
        return self._unverified

    @unverified.setter
    def unverified(self, value: bool):
        self._unverified = value

    @property
    def try_again(self) -> bool:
        return self._try_again

    @try_again.setter
    def try_again(self, value: bool):
        self._try_again = value

    @property
    def account_disabled(self) -> bool:
        return self._account_disabled

    @account_disabled.setter
    def account_disabled(self, value: bool):
        self._account_disabled = value

    @property
    def error(self) -> bool:
        return self._error

    @error.setter
    def error(self, value: bool):
        self._error = value

    @property
    def reuse_old_contact(self) -> bool:
        return self._reuse_old_contact

    @reuse_old_contact.setter
    def reuse_old_contact(self, value: bool):
        self._reuse_old_contact = value
