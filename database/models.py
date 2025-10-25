from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    telegram_id: Column[int] = Column(BigInteger, unique=True, index=True, nullable=False)
    telegram_username: Column[str] = Column(String, nullable=True)
    full_name: Column[str] = Column(String, nullable=False)
    user_lang: Column[str] = Column(String, nullable=False)
    user_role: Column[str] = Column(String, default='user')
    manager_id: Column[str] = Column(String, nullable=True)
    manager_username: Column[str] = Column(String, nullable=True)
    manager_full_name: Column[str] = Column(String, nullable=True)
    ref: Column[int] = Column(BigInteger, nullable=True)
    thread_id: Column[int] = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.now())