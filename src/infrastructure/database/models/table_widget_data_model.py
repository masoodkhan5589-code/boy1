from sqlalchemy import Column, String
from src.infrastructure.database import Base


class TableWidgetDataModel(Base):
    __tablename__ = "table_widget_data"

    id_source = Column(String, primary_key=True)
    uid = Column(String, nullable=True)
    password = Column(String, nullable=True)
    twofactor = Column(String, nullable=True)
    cookie = Column(String, nullable=True)
    bearer_token = Column(String, nullable=True)
    fullname = Column(String, nullable=True)
    contact = Column(String, nullable=True)
    otp = Column(String, nullable=True)
    create_date = Column(String, nullable=True)
    proxy = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    device = Column(String, nullable=True)
    is_verified = Column(String, nullable=True)
    account_status = Column(String, nullable=True)
    total_time = Column(String, nullable=True)
    status = Column(String, nullable=True)
