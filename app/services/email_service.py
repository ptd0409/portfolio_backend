from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings


async def send_email(to_email: str, subject: str, html_content: str) -> None:
    message = EmailMessage()
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content("This email requires HTML support.")
    message.add_alternative(html_content, subtype="html")

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USERNAME,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )


async def send_reset_password_email(to_email: str, reset_link: str) -> None:
    subject = "Reset your password"

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
</head>

<body style="margin:0;background:#f4f6f9;font-family:Arial,Helvetica,sans-serif">

<table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
<tr>
<td align="center">

<table width="520" cellpadding="0" cellspacing="0"
style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.05);">

<tr>
<td style="background:#0b1a3a;padding:28px;text-align:center;color:white;font-size:22px;font-weight:bold;">
Portfolio Admin System
</td>
</tr>

<tr>
<td style="padding:40px">

<h2 style="color:#0b1a3a;margin-top:0">
Reset your password
</h2>

<p style="color:#555;line-height:1.6;font-size:15px">
We received a request to reset your admin password.
Click the button below to create a new password.
</p>

<table cellpadding="0" cellspacing="0" style="margin:30px 0;">
<tr>
<td style="
background:#d2c08d;
border-radius:8px;
padding:14px 28px;
font-weight:bold;
">

<a href="{reset_link}"
style="color:#0b1a3a;text-decoration:none;font-size:15px;">
Reset Password
</a>

</td>
</tr>
</table>

<p style="color:#777;font-size:14px">
This link will expire in 15 minutes.
</p>

<p style="color:#777;font-size:14px">
If you didn't request a password reset, you can safely ignore this email.
</p>

</td>
</tr>

<tr>
<td style="
background:#f7f8fa;
padding:20px;
text-align:center;
font-size:12px;
color:#999;
">
Portfolio Admin System
</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>
"""

    await send_email(to_email, subject, html)

async def send_contact_notification(name: str, email: str, message: str) -> None:
    subject = f"New contact form submission from {name}"
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h2>New Contact Message</h2>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Message:</strong></p>
        <div style="padding: 12px; background: #f5f5f5; border-radius: 8px; white-space: pre-wrap;">
          {message}
        </div>
      </body>
    </html>
    """
    await send_email(settings.SMTP_FROM_EMAIL, subject, html)

async def send_registration_success_email(to_email: str) -> None:
    subject = "Your Admin Account is Ready"

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Admin Account Created</title>
</head>

<body style="margin:0;padding:0;background:#f4f6f9;font-family:Arial,Helvetica,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
<tr>
<td align="center">

<table width="520" cellpadding="0" cellspacing="0"
style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.05);">

<!-- HEADER -->
<tr>
<td style="background:#0b1a3a;padding:28px;text-align:center;color:white;font-size:22px;font-weight:bold;">
Portfolio Admin System
</td>
</tr>

<!-- CONTENT -->
<tr>
<td style="padding:40px">

<h2 style="margin-top:0;color:#0b1a3a;">
Welcome! Your admin account has been created
</h2>

<p style="color:#555;line-height:1.6;font-size:15px">
Your administrator account for the portfolio system is now ready.
You can log in and start managing your projects, uploading images, and editing content.
</p>

<table cellpadding="0" cellspacing="0" style="margin:30px 0;">
<tr>
<td style="
background:#d2c08d;
border-radius:8px;
padding:14px 28px;
font-weight:bold;
">

<a href="http://localhost:5173/admin"
style="color:#0b1a3a;text-decoration:none;font-size:15px;">
Open Admin Dashboard
</a>

</td>
</tr>
</table>

<p style="font-size:14px;color:#777;">
Registered email:
</p>

<p style="
font-weight:bold;
color:#0b1a3a;
font-size:15px;
margin-top:0;
">
{to_email}
</p>

<p style="color:#777;font-size:14px;line-height:1.6;">
If you did not create this account, please ignore this email or contact the administrator.
</p>

</td>
</tr>

<!-- FOOTER -->
<tr>
<td style="
background:#f7f8fa;
padding:20px;
text-align:center;
font-size:12px;
color:#999;
">

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

    await send_email(to_email, subject, html)

async def send_verify_email(to_email: str, verify_link: str) -> None:
    subject = "Verify your admin email"

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Verify Email</title>
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
              <h2 style="margin-top:0;color:#0b1a3a;">Verify your email</h2>

              <p style="color:#555;line-height:1.6;font-size:15px">
                Thanks for registering. Please verify your email before logging in to the admin dashboard.
              </p>

              <table cellpadding="0" cellspacing="0" style="margin:30px 0;">
                <tr>
                  <td style="background:#d2c08d;border-radius:8px;padding:14px 28px;font-weight:bold;">
                    <a href="{verify_link}" style="color:#0b1a3a;text-decoration:none;font-size:15px;">
                      Verify Email
                    </a>
                  </td>
                </tr>
              </table>

              <p style="color:#777;font-size:14px">
                This link will expire in 60 minutes.
              </p>

              <p style="color:#777;font-size:14px">
                If you did not create this account, you can ignore this email.
              </p>
            </td>
          </tr>

          <tr>
            <td style="background:#f7f8fa;padding:20px;text-align:center;font-size:12px;color:#999;">
              Portfolio Admin System
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
    await send_email(to_email, subject, html)