from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine(
    'sqlite:///database.db',
    connect_args={"check_same_thread": False},  # Cần cho đa luồng SQLite
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

from src.infrastructure.database.models import *

Base.metadata.create_all(engine)
