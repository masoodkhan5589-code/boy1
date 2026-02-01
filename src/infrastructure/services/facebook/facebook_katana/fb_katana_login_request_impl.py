import json
import re
import uuid
from typing import Dict, Optional, Tuple

import pyotp

from src.application.interfaces.i_fb_katana_login_request import IFbKatanaLoginRequest
from src.common.utils import compress_to_gzip
from src.domain.dtos.encrypted_password_payload import EncryptPasswordPayload
from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData
from src.infrastructure.clients.request_custom import RequestCustom
from src.infrastructure.services.facebook.facebook_katana.encrypted_password import EncryptedPassword
from src.infrastructure.services.facebook.facebook_katana.fb_request_export_access import FbRequestExportAccess


class FbKatanaLoginRequestImpl(IFbKatanaLoginRequest):
    FB_API_ENDPOINT = 'https://graph.facebook.com/graphql'

    def __init__(self, virtual_device_info_data: VirtualDeviceInfoData, proxy_payload: ProxyPayloadData):
        self.virtual_device_info_data = virtual_device_info_data
        self.proxy_payload = proxy_payload

        self.facebook_access_token_parser = FbRequestExportAccess()
        self.encrypt_password_instance: Optional[EncryptedPassword] = None

    def get_auth(self, facebook_username: str, facebook_password: str, two_factor_key: Optional[str]) -> Tuple:
        self.encrypt_password_instance = EncryptedPassword(EncryptPasswordPayload(password=facebook_password))
        (c_user, cookie, access_token), two_factor_required = self._submit_username_and_password(facebook_username)

        if two_factor_required:
            (c_user, cookie, access_token), action_status = self._submit_two_factor(access_token, two_factor_key)

        return c_user, cookie, access_token

    def _submit_two_factor(self, context: str, two_factor_key: str) -> Tuple[Optional[tuple], bool]:
        client_doc_id = '11994080423068421059028841356'
        fb_api_req_friendly_name = 'FbBloksActionRootQuery-com.bloks.www.two_step_verification.verify_code.async'

        otp_code = pyotp.TOTP(two_factor_key.replace(' ', '')).now()

        client_input_params = {
            "auth_secure_device_id": "",
            "block_store_machine_id": "",
            "code": str(otp_code),
            "should_trust_device": 1,
            "family_device_id": self.virtual_device_info_data.family_device_id,
            "device_id": self.virtual_device_info_data.device_id,
            "cloud_trust_token": None,
            "machine_id": self.virtual_device_info_data.machine_id
        }
        server_params = {
            "INTERNAL__latency_qpl_marker_id": 36707139,
            "block_store_machine_id": None,
            "device_id": self.virtual_device_info_data.device_id,
            "cloud_trust_token": None,
            "challenge": "totp",
            "machine_id": self.virtual_device_info_data.machine_id,
            "INTERNAL__latency_qpl_instance_id": 1.55975297800326E14,
            "two_step_verification_context": context,
            "flow_source": "two_factor_login"
        }

        variables = {
            "params": {
                "params": json.dumps({
                    "params": json.dumps({
                        "client_input_params": client_input_params,
                        "server_params": server_params
                    }, separators=(",", ":"))
                }, separators=(",", ":")),
                "bloks_versioning_id": self.virtual_device_info_data.bloks_versioning_id,
                "app_id": "com.bloks.www.two_step_verification.verify_code.async"
            },
            "scale": "4",
            "nt_context": {
                "using_white_navbar": 'true',
                "pixel_ratio": 4,
                "is_push_on": 'true',
                "styles_id": "e6c6f61b7a86cdf3fa2eaaffa982fbd1",
                "bloks_version": self.virtual_device_info_data.bloks_versioning_id,
            }
        }
        headers = self._prepare_headers("350685531728|62f8ce9f74b12f84c123cc23437a4a32", fb_api_req_friendly_name)
        body = self._prepare_body(variables, client_doc_id, fb_api_req_friendly_name)

        request = RequestCustom(
            url=self.FB_API_ENDPOINT,
            headers=headers,
            body=body,
            proxy=self.proxy_payload.proxy,
            allow_redirects=False
        ).post()

        if request.status_code == 200 and hasattr(request, 'body'):
            return self.facebook_access_token_parser.export(str(request.body)), True

        return None, False

    def _submit_username_and_password(self, facebook_user: str) -> Tuple[Optional[tuple], bool]:  # account access, two factor required
        client_doc_id = '11994080423068421059028841356'
        fb_api_req_friendly_name = 'FbBloksActionRootQuery-com.bloks.www.bloks.caa.login.async.send_login_request'
        public_key_id, public_key = self.encrypt_password_instance.password_key_fetch()

        if not public_key_id or not public_key:
            return None, False

        client_input_params = {
            "sim_phones": [],
            "aymh_accounts": [
                {
                    "profiles": {
                        "id": {
                            "is_derived": 0,
                            "credentials": [],
                            "account_center_id": "",
                            "profile_picture_url": "",
                            "small_profile_picture_url": None,
                            "notification_count": 0,
                            "token": "",
                            "last_access_time": 0,
                            "has_smartlock": 0,
                            "credential_type": "none",
                            "password": "",
                            "from_accurate_privacy_result": 0,
                            "dbln_validated": 0,
                            "user_id": "",
                            "name": "",
                            "nta_eligibility_reason": None,
                            "username": "",
                            "account_source": ""
                        }
                    },
                    "id": ""
                }
            ],
            "secure_family_device_id": self.virtual_device_info_data.event_request_id,
            "has_granted_read_contacts_permissions": 0,
            "auth_secure_device_id": "",
            "has_whatsapp_installed": 0,
            "password": self.encrypt_password_instance.password_encrypt(public_key_id, public_key),
            "sso_token_map_json_string": "",
            "block_store_machine_id": "",
            "cloud_trust_token": None,
            "event_flow": "login_manual",
            "password_contains_non_ascii": "false",
            "sim_serials": [],
            "client_known_key_hash": "",
            "encrypted_msisdn": "",
            "has_granted_read_phone_permissions": 0,
            "app_manager_id": "",
            "should_show_nested_nta_from_aymh": 0,
            "device_id": self.virtual_device_info_data.device_id,
            "login_attempt_count": 1,
            "machine_id": "",
            "accounts_list": [],
            "family_device_id": self.virtual_device_info_data.family_device_id,
            "fb_ig_device_id": [],
            "device_emails": [],
            "try_num": 1,
            "lois_settings": {"lois_token": ""},
            "event_step": "home_page",
            "headers_infra_flow_id": "",
            "openid_tokens": {},
            "contact_point": facebook_user
        }
        server_params = {
            "should_trigger_override_login_2fa_action": 0,
            "is_vanilla_password_page_empty_password": 0,
            "is_from_logged_out": 0,
            "should_trigger_override_login_success_action": 0,
            "login_credential_type": "none",
            "server_login_source": "login",
            "waterfall_id": self.virtual_device_info_data.waterfall_id,
            "two_step_login_type": "one_step_login",
            "login_source": "Login",
            "is_platform_login": 0,
            "pw_encryption_try_count": 1,
            "INTERNAL__latency_qpl_marker_id": 36707139,
            "is_from_aymh": 0,
            "offline_experiment_group": "caa_iteration_v6_perf_fb_2",
            "is_from_landing_page": 0,
            "password_text_input_id": "2to1ro:135",
            "is_from_empty_password": 0,
            "is_from_msplit_fallback": 0,
            "ar_event_source": "login_home_page",
            "username_text_input_id": "2to1ro:134",
            "layered_homepage_experiment_group": None,
            "device_id": self.virtual_device_info_data.device_id,
            "INTERNAL__latency_qpl_instance_id": 1.7076325200239E13,
            "reg_flow_source": "lid_landing_screen",
            "is_caa_perf_enabled": 1,
            "credential_type": "password",
            "is_from_password_entry_page": 0,
            "caller": "gslr",
            "family_device_id": self.virtual_device_info_data.family_device_id,
            "is_from_assistive_id": 0,
            "access_flow_version": "pre_mt_behavior",
            "is_from_logged_in_switcher": 0
        }

        variables = {
            "params": {
                "params": json.dumps({
                    "params": json.dumps({
                        "client_input_params": client_input_params,
                        "server_params": server_params
                    }, separators=(",", ":"))
                }, separators=(",", ":")),
                "bloks_versioning_id": self.virtual_device_info_data.bloks_versioning_id,
                "app_id": "com.bloks.www.bloks.caa.login.async.send_login_request",
            },
            "scale": "1",
            "nt_context": {
                "using_white_navbar": 'true',
                "pixel_ratio": 1,
                "is_push_on": 'true',
                "styles_id": "e6c6f61b7a86cdf3fa2eaaffa982fbd1",
                "bloks_version": self.virtual_device_info_data.bloks_versioning_id,
            }
        }
        headers = self._prepare_headers("350685531728|62f8ce9f74b12f84c123cc23437a4a32", fb_api_req_friendly_name)
        body = self._prepare_body(variables, client_doc_id, fb_api_req_friendly_name)

        request = RequestCustom(
            url=self.FB_API_ENDPOINT,
            headers=headers,
            body=body,
            proxy=self.proxy_payload.proxy,
            allow_redirects=False
        ).post()

        if request.status_code == 200 and hasattr(request, 'body'):
            response_str = str(request.body)
            if 'redirection_to_two_fac' in response_str:
                context_match = re.search(
                    r'INTERNAL_INFRA_screen_id"\), \(bk.action.array.Make, "(.+?)"',
                    response_str.replace('\\', '')
                )

                if context_match:
                    return context_match.group(1), True

            else:
                return self.facebook_access_token_parser.export(str(request.body)), False

        return None, False

    @staticmethod
    def _prepare_body(variables: dict, client_doc_id: str, fb_api_req_friendly_name: str) -> bytes:
        body = {
            "method": "post",
            "pretty": "false",
            "format": "json",
            "purpose": "fetch",
            "server_timestamps": "true",
            "locale": "en_US",
            "fb_api_req_friendly_name": fb_api_req_friendly_name,
            "fb_api_caller_class": "graphservice",
            "client_doc_id": client_doc_id,
            "variables": variables,
            "fb_api_analytics_tags": ["GraphServices"],
            "client_trace_id": str(uuid.uuid4()),
        }
        return compress_to_gzip(body)

    @staticmethod
    def _prepare_headers(fb_access_token: str, fb_api_req_friendly_name: str) -> Dict[str, str]:
        request_analytics_tags = {
            "network_tags": {
                "product": "350685531728",
                "purpose": "fetch",
                "request_category": "graphql",
                "retry_attempt": "0"
            },
            "application_tags": "graphservice"
        }

        headers = {
            "Host": "b-graph.facebook.com",
            "X-Fb-Ta-Logging-Ids": f"graphql:{str(uuid.uuid4())}",
            "Authorization": f"OAuth {fb_access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Graphql-Request-Purpose": "fetch",
            "X-Fb-Sim-Hni": "310270",
            "X-Fb-Background-State": "1",
            "X-Fb-Net-Hni": "310260",
            "X-Fb-Request-Analytics-Tags": json.dumps(request_analytics_tags),
            "X-Graphql-Client-Library": "graphservice",
            "X-Fb-Friendly-Name": fb_api_req_friendly_name,
            "X-Fb-Privacy-Context": "3643298472347298",
            "User-Agent": "[FBAN/FB4A;FBAV/417.0.0.33.65;FBBV/480086166;FBDM/{density=0.75,width=320,height=444};FBLC/en_US;FBRV/0;FBCR/Android;FBMF/Genymobile;FBBD/Custom;FBPN/com.facebook.katana;FBDV/Phone;FBSV/11;FBOP/1;FBCA/arm64-v8a:;]",
            "Content-Encoding": "gzip",
            "X-Fb-Connection-Type": "MOBILE.LTE",
            "X-Fb-Device-Group": "3094",
            "X-Tigon-Is-Retry": "False",
            "Priority": "u=3,i",
            "Accept-Encoding": "gzip, deflate, br",
            "X-Fb-Http-Engine": "Liger",
            "X-Fb-Client-Ip": "True",
            "X-Fb-Server-Cluster": "True",
        }
        return headers
