import secrets
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.email import send_verification_email
from app.core.security import create_access_token, hash_password, now_utc, verify_password
from app.db.deps import get_db
from app.models.auth import EmailVerificationToken, UserEmail
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
)


router = APIRouter(tags=["auth"])


def create_email_verification_token(db: Session, user_id: int) -> str:
    token = secrets.token_hex(32)
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


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    password = req.password

    if "@" not in email:
        raise HTTPException(status_code=400, detail="invalid email")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="password too short")

    existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=409, detail="email already registered")

    user = User(email=email, password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)

    email_row = UserEmail(user_id=user.id, email_verified=False, verified_at=None)
    db.add(email_row)
    db.commit()

    token = create_email_verification_token(db, user.id)
    send_verification_email(to_email=user.email, token=token)

    return {"id": user.id, "email": user.email}


@router.post("/verify-email", response_model=VerifyEmailResponse)
def verify_email(req: VerifyEmailRequest, db: Session = Depends(get_db)):
    row = (
        db.execute(select(EmailVerificationToken).where(EmailVerificationToken.token == req.token))
        .scalar_one_or_none()
    )
    if row is None:
        raise HTTPException(status_code=400, detail="invalid token")
    if row.used_at is not None:
        raise HTTPException(status_code=400, detail="token already used")
    if row.expires_at < now_utc():
        raise HTTPException(status_code=400, detail="token expired")

    row.used_at = now_utc()
    db.add(row)

    email_row = db.execute(select(UserEmail).where(UserEmail.user_id == row.user_id)).scalar_one_or_none()
    if email_row is None:
        email_row = UserEmail(user_id=row.user_id, email_verified=True, verified_at=now_utc())
    else:
        email_row.email_verified = True
        email_row.verified_at = now_utc()
    db.add(email_row)
    db.commit()

    return {"ok": True}


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    password = req.password

    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user is None or not verify_password(password, user.password or ""):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    email_row = db.execute(select(UserEmail).where(UserEmail.user_id == user.id)).scalar_one_or_none()
    if not email_row or not email_row.email_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="email not verified")

    access = create_access_token(user_id=user.id)
    return {"accessToken": access, "tokenType": "bearer"}

