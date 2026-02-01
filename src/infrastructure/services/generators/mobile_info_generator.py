import os
import sys
import json
import random

from src.common import config
from src.infrastructure.localization import get_locale_from_country_code
from src.common.logger import logger
from src.infrastructure.services.generators.virtual_mail_generator import VirtualMailGenerator
from src.infrastructure.services.generators.virtual_phone_generator import VirtualPhoneGenerator


class MobileInfoGenerator:
    def __init__(self, country_code: str):
        self.country_code = (country_code or "US").upper()
        self.hni_file_path = os.path.join(config.data_dir, 'mcc-mnc-list.json')
        self.phone_prefix_file_path = os.path.join(config.data_dir, 'phone-prefix-list.json')
        self.selected_entry = None

        self._load_and_select_entry()
        self._load_phone_prefix_map()

    def _load_phone_prefix_map(self):
        if not os.path.exists(self.phone_prefix_file_path):
            logger.error(f"Phone prefix file not found: {self.phone_prefix_file_path}")
            sys.exit(1)

        with open(self.phone_prefix_file_path, "r", encoding="utf-8") as f:
            self.phone_prefix_map = json.load(f)

    def _load_and_select_entry(self):
        if not os.path.exists(self.hni_file_path):
            logger.error(f"File not found: {self.hni_file_path}")
            sys.exit(1)

        with open(self.hni_file_path, "r", encoding="utf-8") as f:
            all_entries = json.load(f)

        matched_entries = [
            entry for entry in all_entries
            if str(entry.get("countryCode") or "").upper() == self.country_code
               and entry.get("mcc")
               and entry.get("mnc")
        ]

        if not matched_entries:
            matched_entries = [
                entry for entry in all_entries
                if str(entry.get("countryCode") or "").upper() == "US"
                   and entry.get("mcc")
                   and entry.get("mnc")
            ]

        if not matched_entries:
            logger.error("No valid MCC/MNC entries found even for fallback 'US'")
            sys.exit(1)

        self.selected_entry = random.choice(matched_entries)

    def get_hni(self) -> str:
        if not self.selected_entry:
            raise RuntimeError("No MCC/MNC entry selected")
        return f"{self.selected_entry['mcc']}{self.selected_entry['mnc']}"

    def get_mcc(self) -> str:
        return self.selected_entry["mcc"]

    def get_mnc(self) -> str:
        return self.selected_entry["mnc"]

    def get_brand(self) -> str:
        return self.selected_entry.get("brand") or ""

    def get_operator(self) -> str:
        return self.selected_entry.get("operator") or ""

    def get_country_name(self) -> str:
        return self.selected_entry.get("countryName") or ""

    def get_country_code(self) -> str:
        return self.selected_entry.get("countryCode") or ""

    def get_selected_entry(self) -> dict:
        return self.selected_entry

    def get_locale(self) -> str:
        return get_locale_from_country_code(self.country_code)

    def get_phone_number(self) -> str:
        virtual_phone_generator = VirtualPhoneGenerator().create(self.country_code)
        return virtual_phone_generator.contact

    @staticmethod
    def get_email_address() -> str:
        virtual_email_generator = VirtualMailGenerator().create()
        return virtual_email_generator.contact
