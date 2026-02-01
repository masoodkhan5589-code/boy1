from abc import ABC, abstractmethod
from typing import Optional


class IFbHeaderManagement(ABC):
    """
    Interface for managing various Facebook API request headers.
    This abstract class defines the contract for generating different
    types of headers for various Facebook endpoints.
    """

    @staticmethod
    @abstractmethod
    def post_b_graph_non_auth(
        user_agent: str,
        x_fb_friendly_name: str,
        x_fb_device_group: str,
        x_fb_net_hni: str,
        x_fb_sim_hni: str,
        x_fb_ta_logging_ids: str
    ) -> dict:
        """
        Generates headers for a non-authenticated POST request to b-graph.facebook.com.
        """
        pass

    @staticmethod
    @abstractmethod
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
        z_zero_eh: Optional[str],
        x_fb_conn_uuid_client: str
    ) -> dict:
        """
        Generates headers for an authenticated POST request to b-graph.facebook.com.
        """
        pass

    @abstractmethod
    def post_www_non_auth(
        self,
        user_agent: str,
        x_fb_lsd: str,
        x_asbd_id: str = "359341",
        country_code: str = "US"
    ) -> dict:
        """
        Generates headers for a non-authenticated POST request to www.facebook.com.
        """
        pass

    @abstractmethod
    def get_www_non_auth(
        self,
        user_agent: str,
        country_code: str = "US"
    ) -> dict:
        """
        Generates headers for a non-authenticated GET request to www.facebook.com.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_m_facebook_non_auth(
        user_agent: str,
        country_code: str = "US"
    ) -> dict:
        """
        Generates headers for a non-authenticated GET request to m.facebook.com.
        """
        pass

    @staticmethod
    @abstractmethod
    def post_m_facebook_non_auth(
        user_agent: str,
        country_code: str = "US"
    ) -> dict:
        """
        Generates headers for a non-authenticated POST request to m.facebook.com.
        """
        pass
