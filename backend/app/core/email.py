import smtplib
from email.message import EmailMessage

from app.core.config import settings


def build_verification_email(*, verify_url: str) -> tuple[str, str, str]:
    subject = "【Affilido】メールアドレスの確認"

    text = (
        "Affilidoをご利用いただきありがとうございます。\n\n"
        "以下のリンクを開いて、メールアドレスの確認を完了してください。\n\n"
        f"{verify_url}\n\n"
        "このリンクの有効期限が切れている場合は、再度新規登録をお試しください。\n\n"
        "※このメールに心当たりがない場合は、本メールを破棄してください。\n"
    )

    html = f"""\
<!doctype html>
<html lang="ja">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>{subject}</title>
  </head>
  <body style="margin:0;padding:0;background:#f6f7fb;font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;">
    <div style="max-width:640px;margin:0 auto;padding:24px;">
      <div style="background:#ffffff;border:1px solid #e7e9f2;border-radius:12px;padding:24px;">
        <h1 style="margin:0 0 12px;font-size:20px;line-height:1.3;color:#111827;">
          メールアドレスの確認
        </h1>
        <p style="margin:0 0 16px;color:#374151;line-height:1.7;">
          Affilidoをご利用いただきありがとうございます。<br/>
          下のボタンを押して、メールアドレスの確認を完了してください。
        </p>
        <p style="margin:0 0 18px;">
          <a href="{verify_url}"
             style="display:inline-block;background:#2563eb;color:#ffffff;text-decoration:none;padding:12px 18px;border-radius:10px;font-weight:600;">
            メールアドレスを確認する
          </a>
        </p>
        <p style="margin:0 0 8px;color:#6b7280;font-size:13px;line-height:1.7;">
          ボタンが押せない場合は、次のURLをブラウザに貼り付けてください。
        </p>
        <p style="margin:0;color:#111827;font-size:13px;line-height:1.6;word-break:break-all;">
          <a href="{verify_url}" style="color:#2563eb;text-decoration:none;">{verify_url}</a>
        </p>
      </div>
      <p style="margin:14px 4px 0;color:#9ca3af;font-size:12px;line-height:1.6;">
        ※このメールに心当たりがない場合は、本メールを破棄してください。
      </p>
    </div>
  </body>
</html>
"""

    return subject, text, html


def send_verification_email(*, to_email: str, token: str) -> None:
    """
    Mailtrap 等の SMTP を想定した最小実装。
    送信に失敗しても登録処理自体は継続できるよう、例外は飲み込みます。
    """
    verify_url = f"{settings.FRONTEND_BASE_URL}/verify-email?token={token}"
    subject, text, html = build_verification_email(verify_url=verify_url)
    print(f"[mail] verify_url={verify_url}")

    if settings.MAIL_DELIVERY == "log":
        print("[mail] delivery=log (SMTP送信しません)")
        return
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

    msg = EmailMessage()
    if settings.MAIL_FROM_NAME:
        msg["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM_ADDRESS}>"
    else:
        msg["From"] = settings.MAIL_FROM_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(text)
    msg.add_alternative(html, subtype="html")

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

