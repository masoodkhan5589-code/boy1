from dataclasses import dataclass


@dataclass
class VirtualDeviceInfoData:
    waterfall_id: str
    device_id: str
    family_device_id: str
    bloks_versioning_id: str
    user_agent: str
    registration_flow_id: str
    event_request_id: str
    x_fb_net_hni: str
    x_fb_sim_hni: str
    x_fb_device_group: str
    qpl_join_id: str
    headers_flow_id: str
    phone_number: str
    email_address: str
    local_addrs: str
    fb_conn_uuid_client: str
    mcc: str
    mnc: str
    machine_id: str
