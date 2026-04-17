from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.db.database import Base


def utcnow() -> datetime:
    # 依存を増やさずに最小実装（MySQL側のDATETIMEとして保存）
    return datetime.utcnow()


class UserEmail(Base):
    __tablename__ = "user_emails"

    user_id = Column(Integer, primary_key=True)
    email_verified = Column(Boolean, nullable=False, default=False)
    verified_at = Column(DateTime, nullable=True)


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    # URL（クエリ）に載せる想定。衝突確率を下げるため十分長いtokenを使う。
    token = Column(String(64), primary_key=True)
    user_id = Column(Integer, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)


class ProfileInputToken(Base):
    __tablename__ = "profile_input_tokens"

    token = Column(String(64), primary_key=True)
    user_id = Column(Integer, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(Integer, primary_key=True)
    display_name = Column(String(100), nullable=False)
    info = Column(String(1000), nullable=False, default="")
    updated_at = Column(DateTime, nullable=False, default=utcnow)

