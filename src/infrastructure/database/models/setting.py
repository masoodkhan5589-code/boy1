from src.infrastructure.database import Base
from sqlalchemy import Column, Integer, String


class Setting(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True)

    max_threads = Column(Integer, default=1)

    wait_code_timeout = Column(Integer, default=30)
    otp_service_name = Column(String(200))
    otp_service_api_key = Column(String(200))

    proxy_type = Column(String(200))
    proxy_enabled = Column(String(200))
