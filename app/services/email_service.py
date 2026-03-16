from html import escape
from typing import Optional

import httpx

from app.core.config import settings


RESEND_API_URL = "https://api.resend.com/emails"


def _wrap_email_layout(title: str, content_html: str) -> str:
    return f"""\
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{escape(title)}</title>
</head>
<body style="margin:0;padding:0;background:#f4f6f9;font-family:Arial,Helvetica,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
    <tr>
      <td align="center">
        <table width="520" cellpadding="0" cellspacing="0"
          style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.05);">
          <tr>
            <td style="background:#0b1a3a;padding:28px;text-align:center;color:white;font-size:22px;font-weight:bold;">
              Portfolio Admin System
            </td>
          </tr>
          <tr>
            <td style="padding:40px">
              {content_html}
            </td>
          </tr>
          <tr>
            <td style="background:#f7f8fa;padding:20px;text-align:center;font-size:12px;color:#999;">
              Portfolio Admin System<br>
              Automated notification email
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
) -> None:
    payload = {
        "from": settings.EMAIL_FROM,
        "to": [to_email],
        "subject": subject,
        "html": html_content,
        "text": text_content or "This email requires HTML support.",
    }

    headers = {
        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    timeout = httpx.Timeout(20.0, connect=10.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(RESEND_API_URL, json=payload, headers=headers)

    if response.status_code >= 400:
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise RuntimeError(f"Resend send email failed: {response.status_code} - {detail}")


async def send_reset_password_email(to_email: str, reset_link: str) -> None:
    subject = "Reset your password"

    content_html = f"""
      <h2 style="color:#0b1a3a;margin-top:0">Reset your password</h2>
      <p style="color:#555;line-height:1.6;font-size:15px">
        We received a request to reset your admin password.
        Click the button below to create a new password.
      </p>
      <table cellpadding="0" cellspacing="0" style="margin:30px 0;">
        <tr>
          <td style="background:#d2c08d;border-radius:8px;padding:14px 28px;font-weight:bold;">
            <a href="{escape(reset_link, quote=True)}"
               style="color:#0b1a3a;text-decoration:none;font-size:15px;">
              Reset Password
            </a>
          </td>
        </tr>
      </table>
      <p style="color:#777;font-size:14px">This link will expire in 15 minutes.</p>
      <p style="color:#777;font-size:14px">
        If you didn't request a password reset, you can safely ignore this email.
      </p>
    """

    text = (
        f"Reset your password\n\n"
        f"We received a request to reset your admin password.\n"
        f"Open this link to continue: {reset_link}\n\n"
        f"This link will expire in 15 minutes.\n"
        f"If you didn't request a password reset, you can ignore this email."
    )

    html = _wrap_email_layout(subject, content_html)
    await send_email(to_email, subject, html, text)


async def send_verify_email(to_email: str, verify_link: str) -> None:
    subject = "Verify your admin email"

    content_html = f"""
      <h2 style="margin-top:0;color:#0b1a3a;">Verify your email</h2>
      <p style="color:#555;line-height:1.6;font-size:15px">
        Thanks for registering. Please verify your email before logging in to the admin dashboard.
      </p>
      <table cellpadding="0" cellspacing="0" style="margin:30px 0;">
        <tr>
          <td style="background:#d2c08d;border-radius:8px;padding:14px 28px;font-weight:bold;">
            <a href="{escape(verify_link, quote=True)}"
               style="color:#0b1a3a;text-decoration:none;font-size:15px;">
              Verify Email
            </a>
          </td>
        </tr>
      </table>
      <p style="color:#777;font-size:14px">This link will expire in 60 minutes.</p>
      <p style="color:#777;font-size:14px">
        If you did not create this account, you can ignore this email.
      </p>
    """

    text = (
        f"Verify your email\n\n"
        f"Open this link to verify your email: {verify_link}\n\n"
        f"This link will expire in 60 minutes.\n"
        f"If you did not create this account, you can ignore this email."
    )

    html = _wrap_email_layout(subject, content_html)
    await send_email(to_email, subject, html, text)

async def send_contact_notification(name: str, email: str, message: str) -> None:
    subject = f"New contact form submission from {name}"

    html = f"""
    <h2>New Contact Message</h2>
    <p><strong>Name:</strong> {escape(name)}</p>
    <p><strong>Email:</strong> {escape(email)}</p>
    <p><strong>Message:</strong></p>
    <div style="white-space: pre-wrap;">{escape(message)}</div>
    """

    await send_email(settings.CONTACT_RECEIVER_EMAIL, subject, html)