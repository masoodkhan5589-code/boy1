from dataclasses import dataclass


@dataclass
class AccountInitializationConfigData:
    DELAY_BEFORE_UPDATE_INFO: int = 60
    MAX_FRIEND_REQUEST: int = 0
    ENABLE_TWO_FACTOR: bool = False
    ADD_SECONDARY_EMAIL: bool = False
    REMOVE_PRIMARY_EMAIL: bool = False
    ENABLE_UPDATE_BIO: bool = False
    ENABLE_UPDATE_AVATAR: bool = False
