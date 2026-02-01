from dataclasses import fields
from typing import Dict, Any, Optional, Callable, Literal

from src.domain.dtos.ig_table_widget_payload_data import IGTableWidgetPayloadData
from src.domain.dtos.otp_service_response import OTPServiceResponse
from src.domain.dtos.setting_loader_data import SettingLoaderData
from src.domain.dtos.table_widget_payload_data import TableWidgetPayloadData
from src.domain.enums.contact_type import ContactType
from src.infrastructure.contact_management import ContactManagement


class BaseAppHelper:

    def __init__(
            self,
            id_source: str,
            result: Dict[str, Any],
            settings: SettingLoaderData,
            table_data_type: Literal["facebook", "instagram"] = "facebook",
            response_to_table_widget: Optional[Callable] = None
    ):
        if table_data_type == "facebook":
            self._table_data_type = TableWidgetPayloadData
        else:
            self._table_data_type = IGTableWidgetPayloadData

        self._result = result
        self._response_to_table_widget = response_to_table_widget
        self._id_source = id_source
        self._settings = settings
        self._response_to_table_widget = response_to_table_widget

        self._primary_contact = self._init_contact_manager(
            settings.global_setting.otp_service_api_key,
            settings.global_setting.otp_service_name,
            settings.global_setting.wait_code_timeout
        )

        self._primary_otp_response = OTPServiceResponse()

    def update_status(self, success: bool = True, **kwargs) -> bool:
        valid_fields = {f.name for f in fields(self._table_data_type)}
        filtered = {k: v for k, v in kwargs.items() if k in valid_fields}
        self._result.update(filtered)
        data = self._table_data_type(id_source=self._id_source, **self._result)
        if self._response_to_table_widget:
            self._response_to_table_widget(data)
        return success

    @staticmethod
    def _init_contact_manager(
            api_key: str, service_name: str, timeout: int
    ) -> ContactManagement:

        contact_type = ContactType.EMAIL.value.key if 'mail' in service_name else ContactType.PHONE_NUMBER.value.key
        return ContactManagement(
            otp_service_api_key=api_key,
            contact_type=contact_type,
            otp_service=service_name,
            time_out=timeout
        )
