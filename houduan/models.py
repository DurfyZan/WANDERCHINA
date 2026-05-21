from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum

from database import Base


class UserRole(str, Enum):
    ADMIN = "admin"
    ANNOTATOR = "annotator"
    USER = "user"


class UserStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    create_time = Column(DateTime, default=datetime.utcnow)
    last_login_time = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)
    lock_time = Column(DateTime)


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
