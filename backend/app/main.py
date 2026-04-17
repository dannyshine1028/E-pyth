import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
import os
import smtplib
from email.message import EmailMessage
from typing import Literal, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.db.database import Base, SessionLocal, engine
from app.models.auth import EmailVerificationToken, ProfileInputToken, UserEmail, UserProfile
from app.models.user import User


app = FastAPI()

# ローカル開発用: backend/.env を読み込む
load_dotenv()

# Vue (vite:5173) から API (8000) に対してブラウザで通信するための CORS。
# 開発用途のローカル接続を想定し、必要最小限の origin のみ許可します。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def hash_password(password: str) -> str:
    # 既存カラムが `password` しかないため、ここに salt と hash をまとめて保存する
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200_000,
    )
    return f"pbkdf2_sha256${salt}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt, hash_hex = stored.split("$", 2)
    except ValueError:
        return False
    if scheme != "pbkdf2_sha256":
        return False

    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200_000,
    )
    return hmac.compare_digest(dk.hex(), hash_hex)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def now_utc() -> datetime:
    return datetime.utcnow()


def gen_token() -> str:
    # URL（クエリ）に載せるため、比較的読みやすいhexを使う
    return secrets.token_hex(32)


def get_or_create_user_email(db: Session, user_id: int) -> UserEmail:
    status = db.execute(select(UserEmail).where(UserEmail.user_id == user_id)).scalar_one_or_none()
    if status is not None:
        return status

    status = UserEmail(user_id=user_id, email_verified=False, verified_at=None)
    db.add(status)
    db.commit()
    db.refresh(status)
    return status


def user_profile_exists(db: Session, user_id: int) -> bool:
    prof = db.execute(select(UserProfile).where(UserProfile.user_id == user_id)).scalar_one_or_none()
    return prof is not None


def create_email_verification_token(db: Session, user_id: int) -> str:
    # 未使用・未期限が存在すれば再利用して、login のたびに行が増えないようにする
    active = db.execute(
        select(EmailVerificationToken)
        .where(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.used_at.is_(None),
            EmailVerificationToken.expires_at > now_utc(),
        )
        .order_by(EmailVerificationToken.expires_at.desc())
    ).scalar_one_or_none()
    if active is not None:
        return active.token

    token = gen_token()
    expires_at = now_utc() + timedelta(minutes=30)
    row = EmailVerificationToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at,
        used_at=None,
    )
    db.add(row)
    db.commit()
    return token


def create_profile_input_token(db: Session, user_id: int) -> str:
    # 未使用・未期限が存在すれば再利用して、login のたびに行が増えないようにする
    active = db.execute(
        select(ProfileInputToken)
        .where(
            ProfileInputToken.user_id == user_id,
            ProfileInputToken.used_at.is_(None),
            ProfileInputToken.expires_at > now_utc(),
        )
        .order_by(ProfileInputToken.expires_at.desc())
    ).scalar_one_or_none()
    if active is not None:
        return active.token

    token = gen_token()
    expires_at = now_utc() + timedelta(minutes=30)
    row = ProfileInputToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at,
        used_at=None,
    )
    db.add(row)
    db.commit()
    return token


def send_email_verification(to_email: str, token: str) -> None:
    mailer = os.getenv("MAIL_MAILER", "")
    if mailer != "smtp":
        # 設定が無い場合は送信しない（開発用）
        return

    if os.getenv("MAIL_SKIP_SEND", "0") == "1":
        return

    host = os.getenv("MAIL_HOST")
    port_raw = os.getenv("MAIL_PORT")
    username = os.getenv("MAIL_USERNAME")
    password = os.getenv("MAIL_PASSWORD")
    encryption = os.getenv("MAIL_ENCRYPTION", "")
    from_address = os.getenv("MAIL_FROM_ADDRESS")
    from_name = os.getenv("MAIL_FROM_NAME", "")
    frontend_base_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173").rstrip("/")

    if not host or not port_raw or not username or not password or not from_address:
        return

    try:
        port = int(port_raw)
    except ValueError:
        return

    verify_url = f"{frontend_base_url}/verify-email?token={token}"

    msg = EmailMessage()
    if from_name:
        msg["From"] = f"{from_name} <{from_address}>"
    else:
        msg["From"] = from_address
    msg["To"] = to_email
    msg["Subject"] = "メール認証のお願い"

    msg.set_content(
        "以下のリンクからメール認証を完了してください。\n\n"
        f"{verify_url}\n\n"
        "このメールは認証用です。"
    )

    try:
        smtp = smtplib.SMTP(host, port, timeout=10)
        try:
            smtp.ehlo()
            if encryption.lower() == "tls":
                smtp.starttls()
                smtp.ehlo()
            smtp.login(username, password)
            smtp.send_message(msg)
        finally:
            smtp.quit()
    except Exception:
        # メール送信失敗でもユーザー作成は止めない（開発/疎通性優先）
        return


class RegisterRequest(BaseModel):
    email: str
    password: str


class RegisterResponse(BaseModel):
    id: int
    email: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    next: Literal["verify-email", "profile", "dashboard"]
    # 次の画面に遷移するためのトークン（クエリに付与）
    flowToken: Optional[str] = None


class VerifyEmailRequest(BaseModel):
    token: str


class VerifyEmailResponse(BaseModel):
    next: Literal["profile", "dashboard"]
    flowToken: Optional[str] = None


class ProfileRequest(BaseModel):
    token: str
    displayName: str
    info: str = ""


class ProfileResponse(BaseModel):
    ok: bool
    next: Literal["dashboard"]


@app.get("/")
def root():
    return {"message": "Backend OK"}


@app.post("/auth/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    password = req.password

    if "@" not in email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid email")
    if len(password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="password too short")

    existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already registered")

    user = User(email=email, password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    _ = get_or_create_user_email(db, user.id)
    # メール認証リンク（トークン）を登録して送信する
    token = create_email_verification_token(db, user.id)
    send_email_verification(user.email, token)
    return {"id": user.id, "email": user.email}


@app.post("/auth/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    password = req.password

    existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if existing is None or not verify_password(password, existing.password or ""):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    email_status = db.execute(select(UserEmail).where(UserEmail.user_id == existing.id)).scalar_one_or_none()
    if not email_status or not email_status.email_verified:
        # ここではトークン生成やメール送信を行わない（トークンは register で作成・送信済み）
        return {"next": "verify-email", "flowToken": None}

    if user_profile_exists(db, existing.id):
        return {"next": "dashboard", "flowToken": None}

    token = create_profile_input_token(db, existing.id)
    return {"next": "profile", "flowToken": token}


@app.post("/auth/verify-email", response_model=VerifyEmailResponse)
def verify_email(req: VerifyEmailRequest, db: Session = Depends(get_db)):
    token = req.token
    row = db.execute(select(EmailVerificationToken).where(EmailVerificationToken.token == token)).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid token")
    if row.used_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="token already used")
    if row.expires_at < now_utc():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="token expired")

    user_id = row.user_id
    row.used_at = now_utc()

    email_status = get_or_create_user_email(db, user_id)
    email_status.email_verified = True
    email_status.verified_at = now_utc()

    db.add(row)
    db.add(email_status)
    db.commit()

    if user_profile_exists(db, user_id):
        return {"next": "dashboard", "flowToken": None}

    profile_token = create_profile_input_token(db, user_id)
    return {"next": "profile", "flowToken": profile_token}


@app.post("/auth/profile", response_model=ProfileResponse)
def submit_profile(req: ProfileRequest, db: Session = Depends(get_db)):
    token = req.token
    row = db.execute(select(ProfileInputToken).where(ProfileInputToken.token == token)).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid token")
    if row.used_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="token already used")
    if row.expires_at < now_utc():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="token expired")

    display_name = req.displayName.strip()
    if len(display_name) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="displayName is required")

    now = now_utc()
    user_id = row.user_id

    row.used_at = now
    db.add(row)

    existing = db.execute(select(UserProfile).where(UserProfile.user_id == user_id)).scalar_one_or_none()
    if existing is None:
        profile = UserProfile(
            user_id=user_id,
            display_name=display_name,
            info=req.info,
            updated_at=now,
        )
        db.add(profile)
    else:
        existing.display_name = display_name
        existing.info = req.info
        existing.updated_at = now
        db.add(existing)

    db.commit()
    return {"ok": True, "next": "dashboard"}


# 起動時にテーブルを作成（DB が存在しない場合はここで起動に失敗します）
Base.metadata.create_all(bind=engine)