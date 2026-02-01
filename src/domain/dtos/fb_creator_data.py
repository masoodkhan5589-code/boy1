from dataclasses import dataclass

from src.domain.dtos.base_fb_account_infomation_data import BaseFbAccountInformationData
from src.domain.dtos.setting_loader_data import SettingLoaderData


@dataclass
class FbCreatorData:
    id_source: str
    device_id: str
    settings: SettingLoaderData
    fb_account_information_data: BaseFbAccountInformationData
