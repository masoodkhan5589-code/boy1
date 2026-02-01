import os
import random
import uuid
from typing import Literal, Optional, Dict

from src.common import config
from src.common.utils import (
    generate_local_addrs,
    generate_fb_conn_uuid_client,
    generate_machine_id,
    generate_custom_android_id,
    generate_instagram_machine_id, random_non_empty_line,
)
from src.domain.dtos.instagram_virtual_device_info_data import InstagramVirtualDeviceInfoData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData
from src.application.interfaces.i_device_info_generator import IDeviceInfoGenerator
from src.infrastructure.services.generators.mobile_info_generator import MobileInfoGenerator


class VirtualDeviceInfoGenerator(IDeviceInfoGenerator):
    """Sinh dữ liệu thiết bị ảo cho Facebook hoặc Instagram."""

    def __init__(self) -> None:
        self._data_dir = config.data_dir

    # ------------------------
    # Helpers
    # ------------------------
    def _load_app_info(self, files: Dict[str, str]) -> Dict[str, str]:
        """Đọc toàn bộ file cấu hình (user_agent, bloks_versioning_id, v.v)."""
        return {
            key: random_non_empty_line(os.path.join(self._data_dir, fname)) or ""
            for key, fname in files.items()
        }

    # ------------------------
    # Main logic
    # ------------------------
    def generate(
        self,
        app_type: Literal["facebook", "instagram"] = "facebook",
        country_code: Optional[str] = None,
    ) -> VirtualDeviceInfoData | InstagramVirtualDeviceInfoData:

        mobile_gen = MobileInfoGenerator(country_code)

        # --- Dữ liệu chung ---
        common_data = {
            "phone_number": mobile_gen.get_phone_number(),
            "email_address": mobile_gen.get_email_address(),
            "local_addrs": generate_local_addrs(),
        }

        if app_type == "facebook":
            # ------------------------
            # Facebook device info
            # ------------------------
            app_info = self._load_app_info({
                "bloks_versioning_id": "bloks_versioning_id.txt",
                "user_agent": "fb_katana_user_agent.txt",
            })

            hni = mobile_gen.get_hni()

            return VirtualDeviceInfoData(
                bloks_versioning_id=app_info["bloks_versioning_id"],
                user_agent=app_info["user_agent"],
                waterfall_id=str(uuid.uuid4()),
                device_id=str(uuid.uuid4()),
                event_request_id=str(uuid.uuid4()),
                family_device_id=str(uuid.uuid4()),
                registration_flow_id=str(uuid.uuid4()),
                x_fb_net_hni=hni,
                x_fb_sim_hni=hni,
                x_fb_device_group=str(random.randrange(1111, 9999)),
                qpl_join_id=str(uuid.uuid4()),
                headers_flow_id=str(uuid.uuid4()),
                fb_conn_uuid_client=generate_fb_conn_uuid_client(),
                mcc=mobile_gen.get_mcc(),
                mnc=mobile_gen.get_mnc(),
                machine_id=generate_machine_id(),
                **common_data,
            )

        elif app_type == "instagram":
            # ------------------------
            # Instagram device info
            # ------------------------
            app_info = self._load_app_info({
                "bloks_versioning_id": "ig_bloks_versioning_id.txt",
                "user_agent": "ig_user_agent.txt",
                "ig_app_id": "ig_app_id.txt",
            })

            user_agent_final = app_info["user_agent"].replace("{}", mobile_gen.get_locale())

            return InstagramVirtualDeviceInfoData(
                device_uuid=str(uuid.uuid4()),
                bloks_versioning_id=app_info["bloks_versioning_id"],
                user_agent=user_agent_final,
                waterfall_id=str(uuid.uuid4()),
                device_id=generate_custom_android_id(),
                event_request_id=str(uuid.uuid4()),
                family_device_id=str(uuid.uuid4()),
                registration_flow_id=str(uuid.uuid4()),
                headers_flow_id=str(uuid.uuid4()),
                machine_id=generate_instagram_machine_id(),
                x_ig_app_id=app_info["ig_app_id"],
                qe_device_id=str(uuid.uuid4()),
                **common_data,
            )

        else:
            raise ValueError(f"Unsupported app_type: {app_type}")
