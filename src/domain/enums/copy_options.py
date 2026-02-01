from enum import Enum


class CopyOptions(Enum):
    COPY_TYPE_1 = "Uid"
    COPY_TYPE_2 = "Uid|password"
    COPY_TYPE_3 = "Uid|password|2fa"
    COPY_TYPE_4 = "Uid|password|2fa|cookie"
    COPY_TYPE_6 = "Uid|password|cookie|token"
    COPY_TYPE_5 = "Uid|password|2fa|cookie|token"
    COPY_TYPE_7 = "Uid|Password|2fa|cookie|token|mail"
    COPY_TYPE_8 = "Uid|password|cookie|token|mail"
    COPY_TYPE_9 = "Uid|password|2fa|cookie|token|mail|otp"
