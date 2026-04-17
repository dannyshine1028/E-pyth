import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    # DB
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

    # CORS / Frontend
    FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173").rstrip("/")
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # Mail (SMTP)
    MAIL_MAILER: str = os.getenv("MAIL_MAILER", "")
    MAIL_HOST: str | None = os.getenv("MAIL_HOST")
    MAIL_PORT: int | None = int(os.getenv("MAIL_PORT", "0") or "0") or None
    MAIL_USERNAME: str | None = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: str | None = os.getenv("MAIL_PASSWORD")
    MAIL_ENCRYPTION: str = os.getenv("MAIL_ENCRYPTION", "")
    MAIL_FROM_ADDRESS: str | None = os.getenv("MAIL_FROM_ADDRESS")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "")
    MAIL_SKIP_SEND: bool = os.getenv("MAIL_SKIP_SEND", "0") == "1"
    # メール配信モード: "log"（送らずリンクをログに出す） / "smtp"（SMTP送信）
    MAIL_DELIVERY: str = os.getenv("MAIL_DELIVERY", "smtp")


settings = Settings()

