import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ssl import create_default_context


def send_digest_email(
    recipient: str,
    subject: str,
    plain_text: str,
    html_body: str,
) -> None:
    sender = os.environ.get("GMAIL_SENDER")
    app_pw = os.environ.get("GMAIL_APP_PW")
    if not sender or not app_pw:
        raise RuntimeError("Email delivery is not configured")

    message = MIMEMultipart("alternative")
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.attach(MIMEText(plain_text, "plain", "utf-8"))
    message.attach(MIMEText(html_body, "html", "utf-8"))

    context = create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender, app_pw)
        server.sendmail(sender, recipient, message.as_string())
