import json
from typing import Tuple

import requests

from src.application.interfaces.i_fb_katana_confirmation_tut import IFbKatanaConfirmationTut
from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData
from src.infrastructure.services.facebook.facebook_katana.fb_katana_verified_tut_base import \
    FbKatanaVerifiedTutBase


class FbKatanaConfirmationCodeTutImpl(FbKatanaVerifiedTutBase, IFbKatanaConfirmationTut):

    STYLE_ID = "e6c6f61b7a86cdf3fa2eaaffa982fbd1"
    HTTP_ENDPOINT = "https://graph.facebook.com/graphql"

    def __init__(self, virtual_device_info_data: VirtualDeviceInfoData, proxy_payload: ProxyPayloadData):
        super().__init__(virtual_device_info_data, proxy_payload)

        self.session = requests.Session()

    def execute(self, contact: str, confirmation_code: str | int, session: requests.Session, fb_access_token: str) -> Tuple[bool, requests.Session]:
        self.session = session
        return self._confirmation_code(contact, confirmation_code, fb_access_token), self.session

    def _confirmation_code(self, contact: str, confirmation_code: str | int, fb_access_token: str) -> bool:
        app_name = self.bloks_caa_name_manager.confirmation

        client_input_params = {
            "confirmed_cp_and_code": {},
            "code": confirmation_code,
            "fb_ig_device_id": [],
            "device_id": self.virtual_device_info_data.family_device_id,
            "lois_settings": {"lois_token": ""}
        }
        reg_info = {
            "contactpoint_type":"email" if '@' in contact else "phone",
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
            "ig_nta_test_group": None,
            "family_device_id": None,
            "nta_eligibility_reason": None,
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
            "ignore_existing_login": None,
            "ignore_existing_login_from_suma": None,
            "ignore_existing_login_after_errors": None,
            "suggested_first_name": None,
            "suggested_last_name": None,
            "suggested_full_name": None,
            "replace_id_sync_variant": None,
            "is_redirect_from_nta": None,
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
            "youth_regulation_config": None,
            "conf_allow_back_nav_after_change_cp": None,
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
            "ig_partially_created_account_user_id": None,
            "ig_partially_created_account_nonce": None,
            "ig_partially_created_account_nonce_expiry": None,
            "has_seen_suma_landing_page_pre_conf": None,
            "has_seen_suma_candidate_page_pre_conf": None,
            "suma_on_conf_threshold": None,
            "nta_login_footer_variant": None,
            "is_keyboard_autofocus": None,
            "is_spectra_reg": None,
            "spectra_reg_token": None,
            "spectra_reg_guardian_id": None
        }
        if '@' in contact:
            reg_info['contactpoint'] = contact
        else:
            reg_info['contactpoint'] = f"+{contact}" if '+' not in contact else contact

        server_params = {
            "event_request_id": self.virtual_device_info_data.event_request_id,
            "is_from_logged_out": 0,
            "text_input_id": 30457288200049,
            "layered_homepage_experiment_group": None,
            "device_id": None,
            "waterfall_id": self.virtual_device_info_data.waterfall_id,
            "wa_timer_id": "wa_retriever",
            "INTERNAL__latency_qpl_instance_id": 3.0457288200086E13,
            "flow_info": json.dumps(self._prepare_flow_info()),
            "is_platform_login": 0,
            "sms_retriever_started_prior_step": 0,
            "INTERNAL__latency_qpl_marker_id": 36707139,
            "reg_info": json.dumps(reg_info),
            "family_device_id": None,
            "offline_experiment_group": "caa_iteration_v6_perf_fb_2",
            "access_flow_version": "F2_FLOW",
            "is_from_logged_in_switcher": 0,
            "current_step": 10
        }

        req = self.make_request.make_post_request(
            end_point=self.HTTP_ENDPOINT,
            headers=self._make_headers(app_name, fb_access_token),
            body=self._make_body_request(client_input_params, server_params, app_name),
            proxy=self.proxy_payload.proxy,
            verify_ssl=True,
            session=self.session
        )

        if req and req.status_code == 200 and hasattr(req, 'body') and 'confirm_contact_point_finished' in req.body:
            return True
        return False
