import json
import uuid

from src.common.bloks_caa_name_constants import BloksCaaNameConstants
from src.common.utils import compress_to_gzip
from src.domain.dtos.proxy_payload_data import ProxyPayloadData
from src.domain.dtos.virtual_device_info_data import VirtualDeviceInfoData

from src.infrastructure.helpers.make_requests import MakeRequest
from src.infrastructure.localization import get_locale_from_country_code


class FbKatanaVerifiedTutBase:

    STYLE_ID = "e6c6f61b7a86cdf3fa2eaaffa982fbd1"
    HTTP_ENDPOINT = "https://graph.facebook.com/graphql"

    def __init__(self, virtual_device_info_data: VirtualDeviceInfoData, proxy_payload: ProxyPayloadData):
        self.virtual_device_info_data = virtual_device_info_data
        self.proxy_payload = proxy_payload
        self.local = get_locale_from_country_code(proxy_payload.country_code)

        self._bloks_action_base = "FbBloksActionRootQuery-{}"
        self.bloks_caa_name_manager = BloksCaaNameConstants()

        self.make_request = MakeRequest()

    def _make_headers(self, app_name: str, fb_access_token: str) -> dict:
        return {
            "Host": "graph.facebook.com",
            "X-Fb-Ta-Logging-Ids": f"graphql:{str(uuid.uuid4())}",
            "X-Fb-Rmd": "state=URL_ELIGIBLE",
            "Authorization": f"OAuth {fb_access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Graphql-Request-Purpose": "fetch",
            "X-Fb-Sim-Hni": self.virtual_device_info_data.x_fb_sim_hni,
            "X-Fb-Background-State": "1",
            "X-Fb-Net-Hni": self.virtual_device_info_data.x_fb_net_hni,
            "X-Fb-Request-Analytics-Tags": '{"network_tags":{"product":"350685531728","purpose":"fetch","request_category":"graphql","retry_attempt":"0"},"application_tags":"graphservice"}',
            "X-Graphql-Client-Library": "graphservice",
            "X-Fb-Friendly-Name": self._bloks_action_base.format(app_name),
            "X-Fb-Privacy-Context": "3643298472347298",
            "User-Agent": self.virtual_device_info_data.user_agent,
            "Content-Encoding": "gzip",
            "X-Fb-Connection-Type": "WIFI",
            "X-Fb-Device-Group": self.virtual_device_info_data.x_fb_device_group,
            "X-Tigon-Is-Retry": "False",
            "Priority": "u=3,i",
            "Accept-Encoding": "gzip, deflate, br",
            "X-Fb-Http-Engine": "Liger",
            "X-Fb-Client-Ip": "True",
            "X-Fb-Server-Cluster": "True"
        }

    def _make_body_request(
            self,
            client_input_params: dict,
            server_params: dict,
            app_name: str,
            client_doc_id: str = "11994080423068421059028841356"
    ):
        base_body = {
            "method": "post",
            "pretty": "false",
            "format": "json",
            "server_timestamps": "true",
            "locale": self.local,
            "purpose": "fetch",
            "fb_api_req_friendly_name": self._bloks_action_base.format(app_name),
            "fb_api_caller_class": "graphservice",
            "client_doc_id": client_doc_id,
            "fb_api_analytics_tags": json.dumps(["GraphServices"]),
            "client_trace_id": str(uuid.uuid4()),
            "variables": json.dumps({
                "params": {
                    "params": json.dumps({
                        "params": json.dumps({
                            "client_input_params": client_input_params,
                            "server_params": server_params
                        })
                    }),
                    "bloks_versioning_id": self.virtual_device_info_data.bloks_versioning_id,
                    "app_id": app_name
                },
                "scale": "1",
                "nt_context": {
                    "using_white_navbar": True,
                    "pixel_ratio": 1,
                    "is_push_on": True,
                    "styles_id": self.STYLE_ID,
                    "bloks_version": self.virtual_device_info_data.bloks_versioning_id
                }
            }),
        }

        return compress_to_gzip(base_body)

    @staticmethod
    def _prepare_flow_info() -> dict:
        return {"flow_name": "new_to_family_fb_default", "flow_type": "ntf"}
