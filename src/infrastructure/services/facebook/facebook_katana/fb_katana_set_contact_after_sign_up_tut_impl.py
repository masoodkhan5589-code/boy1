import json
from typing import Tuple

import requests

from src.application.interfaces.i_fb_katana_add_contact_after_sign_up_tut import IFbKatanaAddContactAfterSignUpTut
from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData
from src.infrastructure.services.facebook.facebook_katana.fb_katana_verified_tut_base import \
    FbKatanaVerifiedTutBase


class FbKatanaSetContactAfterSignUpTutImpl(FbKatanaVerifiedTutBase, IFbKatanaAddContactAfterSignUpTut):
    """TUT Add mail hybrid (save data)"""
    STYLE_ID = "e6c6f61b7a86cdf3fa2eaaffa982fbd1"
    HTTP_ENDPOINT = "https://graph.facebook.com/graphql"

    def __init__(self, virtual_device_info_data: VirtualDeviceInfoData, proxy_payload: ProxyPayloadData):
        super().__init__(virtual_device_info_data, proxy_payload)

        self.session = requests.Session()

    def execute(self, contact: str, fb_access_token: str, session: requests.Session) -> Tuple[bool, requests.Session]:
        self.session = session
        return self._change_email(contact, fb_access_token), self.session

    def _change_email(self, primary_email: str, fb_access_token: str) -> bool:
        app_name = self.bloks_caa_name_manager.add_mail if '@' in primary_email else self.bloks_caa_name_manager.add_phone

        reg_info = {
            "contact point_type": "email" if '@' in primary_email else "phone",
            "first_name": None,
            "last_name": None,
            "full_name": None,
            "ar_contactpoint": None,
            "is_using_unified_cp": None,
            "unified_cp_screen_variant": None,
            "is_cp_auto_confirmed": None,
            "is_cp_auto_confirmable": None,
            "confirmation_code": None,
            "birthday": None,
            "birthday_derived_from_age": None,
            "did_use_age": None,
            "gender": None,
            "use_custom_gender": None,
            "custom_gender": None,
            "encrypted_password": None,
            "username": None,
            "username_prefill": None,
            "fb_conf_source": None,
            "device_id": None,
            "ig4a_qe_device_id": None,
            "family_device_id": None,
            "youth_consent_decision_time": None,
            "user_id": None,
            "safetynet_token": None,
            "safetynet_response": None,
            "machine_id": None,
            "profile_photo": None,
            "profile_photo_id": None,
            "profile_photo_upload_id": None,
            "avatar": None,
            "email_oauth_token_no_contact_perm": None,
            "email_oauth_token": None,
            "email_oauth_tokens": None,
            "should_skip_two_step_conf": None,
            "openid_tokens_for_testing": None,
            "encrypted_msisdn": None,
            "encrypted_msisdn_for_safetynet": None,
            "cached_headers_safetynet_info": None,
            "should_skip_headers_safetynet": None,
            "headers_last_infra_flow_id": None,
            "headers_last_infra_flow_id_safetynet": None,
            "headers_flow_id": None,
            "was_headers_prefill_available": None,
            "sso_enabled": None,
            "existing_accounts": None,
            "used_ig_birthday": None,
            "sync_info": None,
            "create_new_to_app_account": None,
            "skip_session_info": None,
            "ck_error": None,
            "ck_id": None,
            "ck_nonce": None,
            "should_save_password": None,
            "should_show_error_msg": None,
            "horizon_synced_username": None,
            "fb_access_token": None,
            "horizon_synced_profile_pic": None,
            "is_identity_synced": None,
            "is_msplit_reg": None,
            "user_id_of_msplit_creator": None,
            "msplit_creator_nonce": None,
            "dma_data_combination_consent_given": None,
            "xapp_accounts": None,
            "fb_device_id": None,
            "fb_machine_id": None,
            "ig_device_id": None,
            "ig_machine_id": None,
            "should_skip_nta_upsell": None,
            "big_blue_token": None,
            "skip_sync_step_nta": None,
            "caa_reg_flow_source": None,
            "ig_authorization_token": None,
            "full_sheet_flow": None,
            "crypted_user_id": None,
            "is_caa_perf_enabled": None,
            "is_preform": None,
            "ignore_suma_check": None,
            "dismissed_login_upsell_with_cna": None,
            "ignore_existing_login": None,
            "ignore_existing_login_from_suma": None,
            "ignore_existing_login_after_errors": None,
            "suggested_first_name": None,
            "suggested_last_name": None,
            "suggested_full_name": None,
            "frl_authorization_token": None,
            "post_form_errors": None,
            "skip_step_without_errors": None,
            "existing_account_exact_match_checked": None,
            "existing_account_fuzzy_match_checked": None,
            "email_oauth_exists": None,
            "confirmation_code_send_error": None,
            "is_too_young": None,
            "source_account_type": None,
            "whatsapp_installed_on_client": None,
            "confirmation_medium": None,
            "source_credentials_type": None,
            "source_cuid": None,
            "source_account_reg_info": None,
            "soap_creation_source": None,
            "source_account_type_to_reg_info": None,
            "registration_flow_id": None,
            "should_skip_youth_tos": None,
            "is_youth_regulation_flow_complete": None,
            "is_on_cold_start": None,
            "email_prefilled": None,
            "cp_confirmed_by_auto_conf": None,
            "auto_conf_info": None,
            "in_sowa_experiment": None,
            "eligible_to_flash_call_in_ig4a": None,
            "attempted_silent_auth_in_fb": None,
            "youth_regulation_config": None,
            "conf_allow_back_nav_after_change_cp": True,
            "conf_bouncing_cliff_screen_type": None,
            "conf_show_bouncing_cliff": None,
            "is_msplit_neutral_choice": None,
            "msg_previous_cp": None,
            "ntp_import_source_info": None,
            "flash_call_permissions_status": None,
            "attestation_result": None,
            "request_data_and_challenge_nonce_string": None,
            "confirmed_cp_and_code": None,
            "notification_callback_id": None,
            "reg_suma_state": None,
            "should_show_spi_before_conf": None,
            "google_oauth_account": None,
            "is_reg_request_from_ig_suma": None,
            "device_emails": None,
            "is_toa_reg": None,
            "is_threads_public": None,
            "spc_import_flow": None,
            "caa_play_integrity_attestation_result": None,
            "client_known_key_hash": None,
            "flash_call_provider": None,
            "spc_birthday_input": None,
            "failed_birthday_year_count": None,
            "user_presented_medium_source": None,
            "user_opted_out_of_ntp": None,
            "is_from_registration_reminder": None,
            "show_youth_reg_in_ig_spc": None,
            "fb_suma_combined_landing_candidate_variant": None,
            "fb_suma_is_high_confidence": None,
            "screen_visited": ["CAA_REG_CONFIRMATION_SCREEN"],
            "fb_email_login_upsell_skip_suma_post_tos": None,
            "fb_suma_is_from_email_login_upsell": None,
            "fb_suma_is_from_phone_login_upsell": None,
            "fb_suma_login_upsell_skipped_warmup": None,
            "fb_suma_login_upsell_show_list_cell_link": None,
            "should_prefill_cp_in_ar": None,
            "pp_to_nux_eligible": None,
            "ig_partially_created_account_user_id": None,
            "ig_partially_created_account_nonce": None,
            "ig_partially_created_account_nonce_expiry": None,
            "has_seen_suma_landing_page_pre_conf": None,
            "has_seen_suma_candidate_page_pre_conf": None,
            "suma_on_conf_threshold": None,
            "is_keyboard_autofocus": None,
            "welcome_ar_entrypoint": None,
            "is_spectra_reg": None,
            "spectra_reg_token": None,
            "spectra_reg_guardian_id": None,
            "th_profile_photo_token": None
        }
        if '@' in primary_email:
            reg_info['contactpoint'] = primary_email
        else:
            reg_info['contactpoint'] = f"+{primary_email}" if '+' not in primary_email else primary_email

        server_params = {
            "event_request_id": self.virtual_device_info_data.event_request_id,
            "is_from_logged_out": 0,
            "text_input_id": 22244490000124,
            "layered_homepage_experiment_group": None,
            "device_id": None,
            "waterfall_id": self.virtual_device_info_data.waterfall_id,
            "INTERNAL__latency_qpl_instance_id": 2.2244490000126E13,
            "flow_info": json.dumps(self._prepare_flow_info(), separators=(',', ':')),
            "is_platform_login": 0,
            "INTERNAL__latency_qpl_marker_id": 36707139,
            "reg_info": json.dumps(reg_info, separators=(',', ':')),
            "family_device_id": None,
            "offline_experiment_group": "caa_iteration_v6_perf_fb_2",
            "cp_funnel": 1,
            "cp_source": 1,
            "access_flow_version": "F2_FLOW",
            "is_from_logged_in_switcher": 0,
            "current_step": 10
        }
        client_input_params = {
            "device_id": self.virtual_device_info_data.device_id,
            "was_headers_prefill_available": 0,
            "login_upsell_phone_list": [],
            "whatsapp_installed_on_client": 0,
            "msg_previous_cp": "",
            "switch_cp_first_time_loading": 1,
            "accounts_list": [],
            "confirmed_cp_and_code": {},
            "country_code": "",
            "family_device_id": self.virtual_device_info_data.family_device_id,
            "block_store_machine_id": "",
            "fb_ig_device_id": [],
            "lois_settings": {"lois_token": ""},
            "cloud_trust_token": None,
            "was_headers_prefill_used": 0,
            "headers_infra_flow_id": "",
            "build_type": "",
            "encrypted_msisdn": "",
            "switch_cp_have_seen_suma": 0
        }

        if '@' in primary_email:
            client_input_params['email'] = primary_email
        else:
            client_input_params['phone'] = f"+{primary_email}" if '+' not in primary_email else primary_email

        req = self.make_request.make_post_request(
            end_point=self.HTTP_ENDPOINT,
            headers=self._make_headers(app_name, fb_access_token),
            body=self._make_body_request(client_input_params, server_params, app_name),
            proxy=self.proxy_payload.proxy,
            verify_ssl=True,
            session=self.session
        )

        if req and req.status_code == 200 and hasattr(req, 'body') and 'confirmation' in req.body:
            self.session = req.session
            return True
        return False
