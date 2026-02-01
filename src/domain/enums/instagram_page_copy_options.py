from enum import Enum


class InstagramPageCopyOptions(Enum):
    COPY_TYPE_1 = "Username"
    COPY_TYPE_2 = "Username|password"
    COPY_TYPE_3 = "Username|password|2fa"
    COPY_TYPE_4 = "Username|password|2fa|cookie"
    COPY_TYPE_5 = "Username|password|2fa|cookie|token"
    COPY_TYPE_6 = "Username|password|cookie|token"
    COPY_TYPE_7 = "Username|Password|2fa|cookie|token|mail"
    COPY_TYPE_8 = "Username|password|cookie|token|mail"
