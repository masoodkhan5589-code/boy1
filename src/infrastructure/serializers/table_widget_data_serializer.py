from src.domain.dtos.table_widget_payload_data import TableWidgetPayloadData


class TableWidgetDataSerializer:
    FIELDS = [
        "id_source",
        "uid",
        "password",
        "twofactor",
        "cookie",
        "bearer_token",
        "fullname",
        "contact",
        "otp",
        "create_date",
        "proxy",
        "ip_address",
        "is_verified",
        "account_status",
        "total_time",
        "status",
    ]

    @classmethod
    def to_pipe_string(cls, data: TableWidgetPayloadData) -> str:
        values = [getattr(data, field, "") or "" for field in cls.FIELDS]
        return "|".join(values)

    @classmethod
    def from_pipe_string(cls, data_str: str) -> TableWidgetPayloadData:
        parts = data_str.split("|")
        # tự bổ sung rỗng nếu thiếu cột
        while len(parts) < len(cls.FIELDS):
            parts.append("")

        kwargs = dict(zip(cls.FIELDS, parts))
        return TableWidgetPayloadData(**kwargs)
