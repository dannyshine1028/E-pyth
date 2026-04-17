import smtplib
from email.message import EmailMessage

from app.core.config import settings


def send_verification_email(*, to_email: str, token: str) -> None:
    """
    Mailtrap 等の SMTP を想定した最小実装。
    送信に失敗しても登録処理自体は継続できるよう、例外は飲み込みます。
    """
    if settings.MAIL_SKIP_SEND:
        print("[mail] skipped: MAIL_SKIP_SEND=1")
        return
    if settings.MAIL_MAILER != "smtp":
        print(f"[mail] skipped: MAIL_MAILER={settings.MAIL_MAILER!r}")
        return
    if (
        not settings.MAIL_HOST
        or not settings.MAIL_PORT
        or not settings.MAIL_USERNAME
        or not settings.MAIL_PASSWORD
        or not settings.MAIL_FROM_ADDRESS
    ):
        print("[mail] skipped: SMTP settings missing")
        return

    verify_url = f"{settings.FRONTEND_BASE_URL}/verify-email?token={token}"

    msg = EmailMessage()
    if settings.MAIL_FROM_NAME:
        msg["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM_ADDRESS}>"
    else:
        msg["From"] = settings.MAIL_FROM_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = "メール認証のお願い"
    msg.set_content(
        "以下のリンクからメール認証を完了してください。\n\n"
        f"{verify_url}\n\n"
        "このメールは認証用です。"
    )

    try:
        print(f"[mail] sending to={to_email} host={settings.MAIL_HOST}:{settings.MAIL_PORT}")
        smtp = smtplib.SMTP(settings.MAIL_HOST, settings.MAIL_PORT, timeout=10)
        try:
            smtp.ehlo()
            if settings.MAIL_ENCRYPTION.lower() == "tls":
                smtp.starttls()
                smtp.ehlo()
            smtp.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            smtp.send_message(msg)
            print("[mail] sent")
        finally:
            smtp.quit()
    except Exception as e:
        print(f"[mail] failed: {type(e).__name__}: {e}")
        return

