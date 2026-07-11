import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from config import settings

logger = logging.getLogger("app.email")


def send_digest_email(to_email: str, subject: str, html_content: str) -> bool:
    sender = settings.smtp_user
    password = settings.smtp_password
    if not sender or not password:
        logger.warning("Gmail credentials not configured; email not sent to %s", to_email)
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, password)
            smtp.sendmail(sender, [to_email], msg.as_string())
        logger.info("Sent digest email to %s", to_email)
        return True
    except Exception as exc:
        logger.exception("Failed to send email to %s: %s", to_email, exc)
        return False


def render_digest_html(subject: str, greeting: str, items_html: str) -> str:
    from datetime import datetime
    date_str = datetime.now().strftime("%B %d, %Y")
    template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{subject}</title>
<style>
    body {{ background-color: #1a1a2e; color: #eaeaea; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; margin: 0; padding: 0; }}
    .container {{ max-width: 680px; margin: 20px auto; background: #16213e; border-radius: 12px; padding: 32px; border: 1px solid #0f3460; }}
    .header {{ border-bottom: 1px solid #0f3460; padding-bottom: 16px; margin-bottom: 24px; }}
    .header h1 {{ color: #e94560; font-size: 22px; margin: 0; }}
    .item {{ background: #1a1a2e; border-left: 4px solid #e94560; padding: 14px 18px; margin-bottom: 16px; border-radius: 0 8px 8px 0; }}
    .item h3 {{ margin: 0 0 6px; font-size: 16px; color: #ffffff; }}
    .item a {{ color: #53a8b6; text-decoration: none; font-size: 14px; }}
    .item a:hover {{ text-decoration: underline; }}
    .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #888; }}
</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Your AI Daily Digest</h1>
            <p style="margin: 6px 0 0; color: #aaa; font-size: 14px;">{greeting}</p>
        </div>
        {items_html}
        <div class="footer">
            <p>Generated on {date_str} • AI News Digest</p>
        </div>
    </div>
</body>
</html>"""
    return template


def build_items_html(items: list[dict]) -> str:
    html_parts = []
    for item in items:
        score = item.get("score")
        score_str = f" · ⬆ {score}" if score else ""
        html_parts.append(
            f"""<div class="item">
            <h3>{item['title']}</h3>
            <a href="{item['url']}" target="_blank">Read more{score_str}</a>
        </div>"""
        )
    return "\n".join(html_parts)
