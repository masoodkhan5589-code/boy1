import re

from src.application.interfaces.i_fb_header_maagement import IFbHeaderManagement
from src.infrastructure.localization import get_accept_language


class FbHeaderManagement(IFbHeaderManagement):

    @staticmethod
    def post_b_graph_non_auth(
            user_agent: str,
            x_fb_friendly_name: str,
            x_fb_device_group: str,
            x_fb_net_hni: str,
            x_fb_sim_hni: str,
            x_fb_ta_logging_ids: str
    ) -> dict:
        return {
            "X-Fb-Ta-Logging-Ids": f"graphql:{x_fb_ta_logging_ids}",
            "Authorization": "OAuth 350685531728|62f8ce9f74b12f84c123cc23437a4a32",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Graphql-Request-Purpose": "fetch",
            "X-Fb-Sim-Hni": x_fb_sim_hni,
            "X-Fb-Background-State": "1",
            "X-Fb-Net-Hni": x_fb_net_hni,
            "X-Fb-Request-Analytics-Tags": '{"network_tags":{"product":"350685531728","purpose":"fetch","request_category":"graphql","retry_attempt":"0"},"application_tags":"graphservice"}',
            "X-Graphql-Client-Library": "graphservice",
            "X-Fb-Friendly-Name": x_fb_friendly_name,
            "X-Fb-Privacy-Context": "3643298472347298",
            "User-Agent": user_agent,
            "Content-Encoding": "gzip",
            "X-Fb-Connection-Type": "WIFI",
            "X-Fb-Device-Group": x_fb_device_group,
            "X-Tigon-Is-Retry": "False",
            "Priority": "u=3,i",
            "Accept-Encoding": "gzip, deflate, br",
            "X-Fb-Http-Engine": "Liger",
            "X-Fb-Client-Ip": "True",
            "X-Fb-Server-Cluster": "True",
        }

    @staticmethod
    def post_b_graph_via_auth(
            user_agent: str,
            x_fb_friendly_name: str,
            x_fb_device_group: str,
            x_fb_net_hni: str,
            x_fb_sim_hni: str,
            device_id: str,
            family_device_id: str,
            fb_access_token: str,
            local_ip_address: str,
            z_zero_eh: str,
            x_fb_conn_uuid_client: str
    ) -> dict:
        headers = {
            "X-Meta-Enable-Tasos-Ss-Bwe": "1",
            "X-Fb-Rmd": "state=URL_ELIGIBLE",
            "X-Fb-Qpl-Active-Flows-Json": '{"schema_version":"v2","inprogress_qpls":[],"snapshot_attributes":{}}',
            "X-Fb-Network-Properties": f";;Validated;LocalAddrs=/{local_ip_address},;",
            "Priority": "u=0",
            "X-Fb-Connection-Type": "WIFI",
            "App-Scope-Id-Header": device_id,
            "Authorization": f"OAuth {fb_access_token}",
            "X-Fb-Sim-Hni": x_fb_sim_hni,
            "X-Fb-Net-Hni": x_fb_net_hni,
            "Content-Encoding": "gzip",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Graphql-Client-Library": "graphservice",
            "X-Tigon-Is-Retry": "False",
            "X-Fb-Device-Group": x_fb_device_group,
            "X-Graphql-Request-Purpose": "fetch",
            "X-Zero-F-Device-Id": family_device_id,
            "X-Fb-Friendly-Name": x_fb_friendly_name,
            "User-Agent": user_agent,
            "X-Fb-Request-Analytics-Tags": '{"network_tags":{"product":"350685531728","purpose":"fetch","request_category":"graphql","retry_attempt":"0"},"application_tags":"graphservice"}',
            "Accept-Encoding": "gzip, deflate, br",
            "X-Fb-Http-Engine": "Tigon/Liger",
            "X-Fb-Client-Ip": "True",
            "X-Fb-Server-Cluster": "True",
            "X-Fb-Conn-Uuid-Client": x_fb_conn_uuid_client
        }

        if z_zero_eh:
            headers["X-Zero-Eh"] = z_zero_eh

        return headers

    def post_www_non_auth(
            self,
            user_agent: str,
            x_fb_lsd: str,
            x_asbd_id: str = "359341",
            country_code: str = "US"
    ) -> dict:
        user_agent_information = self._platform_mapping(user_agent)

        return {
            "Accept-Language": get_accept_language(country_code),
            "Sec-Ch-Ua": user_agent_information.get("sec_ch_ua"),
            "Sec-Ch-Ua-Mobile": user_agent_information.get("is_mobile"),
            "Sec-Ch-Ua-Platform": user_agent_information.get("platform"),
            "X-Asbd-Id": x_asbd_id,
            "X-Fb-Lsd": x_fb_lsd,
            "User-Agent": user_agent,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "Origin": "https://www.facebook.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Encoding": "gzip, deflate, br",
            "Priority": "u=1, i",
        }

    def get_www_non_auth(
            self,
            user_agent: str,
            country_code: str = "US"
    ) -> dict:
        user_agent_information = self._platform_mapping(user_agent)

        return {
            "Accept-Language": get_accept_language(country_code),
            "Sec-Ch-Ua": user_agent_information.get("sec_ch_ua"),
            "Sec-Ch-Ua-Mobile": user_agent_information.get("is_mobile"),
            "Sec-Ch-Ua-Platform": user_agent_information.get("platform"),
            "User-Agent": user_agent,
            "Origin": "https://www.facebook.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Encoding": "gzip, deflate, br",
            "Priority": "u=1, i",
            'sec-fetch-dest': 'document',
        }

    @staticmethod
    def get_m_facebook_non_auth(
            user_agent: str,
            country_code: str = "US"
    ) -> dict:
        return {
            "Accept-Language": get_accept_language(country_code),
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Accept-Encoding": "gzip, deflate, br",
            "Priority": "u=0, i"
        }

    @staticmethod
    def post_m_facebook_non_auth(
            user_agent: str,
            country_code: str = "US"
    ) -> dict:
        return {
            "Sec-Ch-Prefers-Color-Scheme": "dark",
            "Accept-Language": get_accept_language(country_code),
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "User-Agent": user_agent,
            "Accept": "*/*",
            "Origin": "https://m.facebook.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Encoding": "gzip, deflate, br",
            "Priority": "u=1, i"
        }

    @staticmethod
    def _platform_mapping(user_agent: str) -> dict:
        platform_mapping = {
            "Windows": '"Windows"',
            "Macintosh": '"macOS"',
            "Linux": '"Linux"',
            "Android": '"Android"',
            "iPhone": '"iOS"',
            "iPad": '"iOS"'
        }
        detected_platform = next((platform_mapping[k] for k in platform_mapping if k in user_agent), '"Unknown"')
        is_mobile = "?1" if "Mobile" in user_agent or "Android" in user_agent or "iPhone" in user_agent else "?0"
        match = re.search(r"Chrome/(\d+)", user_agent)
        chrome_version = match.group(1) if match else "133"
        sec_ch_ua = f'"Not(A:Brand";v="99", "Google Chrome";v="{chrome_version}", "Chromium";v="{chrome_version}")'

        return {"platform": detected_platform, "is_mobile": is_mobile, "sec_ch_ua": sec_ch_ua}
