from dataclasses import dataclass


@dataclass
class InstagramVirtualDeviceInfoData:
    device_uuid: str
    waterfall_id: str
    device_id: str
    family_device_id: str
    bloks_versioning_id: str
    user_agent: str
    registration_flow_id: str
    event_request_id: str
    x_ig_app_id: str
    headers_flow_id: str
    phone_number: str
    email_address: str
    local_addrs: str
    machine_id: str
    qe_device_id: str
