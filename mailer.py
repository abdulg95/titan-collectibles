import os, smtplib, ssl, json, requests
from email.message import EmailMessage

MAIL_BACKEND = os.getenv('MAIL_BACKEND', 'console')
SENDER = os.getenv('EMAIL_SENDER', 'no-reply@example.com')

def send_email(to: str, subject: str, html: str, text: str | None = None):
    text = text or "Please view this email in an HTML-capable client."
    if MAIL_BACKEND == 'console':
        print("\n=== EMAIL (console) ===")
        print("To:", to)
        print("Subject:", subject)
        print("HTML:\n", html)
        print("=======================\n")
        return True

    if MAIL_BACKEND == 'sendgrid':
        api_key = os.getenv('SENDGRID_API_KEY')
        if not api_key: raise RuntimeError("SENDGRID_API_KEY missing")
        resp = requests.post(
            'https://api.sendgrid.com/v3/mail/send',
            headers={'Authorization': f'Bearer {api_key}',
                     'Content-Type': 'application/json'},
            data=json.dumps({
                "personalizations":[{"to":[{"email":to}]}],
                "from":{"email":SENDER},
                "subject":subject,
                "content":[
                    {"type":"text/plain", "value":text},
                    {"type":"text/html", "value":html}
                ],
                "tracking_settings": {
                    "click_tracking": {
                        "enable": False
                    },
                    "open_tracking": {
                        "enable": False
                    }
                }
            })
        )
        if resp.status_code >= 300:
            raise RuntimeError(f"SendGrid error: {resp.status_code} {resp.text}")
        return True

    if MAIL_BACKEND == 'smtp':
        host = os.getenv('SMTP_HOST'); port = int(os.getenv('SMTP_PORT', '587'))
        user = os.getenv('SMTP_USER'); pwd = os.getenv('SMTP_PASS')
        use_tls = os.getenv('SMTP_USE_TLS', 'True') == 'True'
        msg = EmailMessage()
        msg['From'] = SENDER
        msg['To'] = to
        msg['Subject'] = subject
        msg.set_content(text)
        msg.add_alternative(html, subtype='html')
        if use_tls:
            ctx = ssl.create_default_context()
            with smtplib.SMTP(host, port) as s:
                s.starttls(context=ctx)
                if user: s.login(user, pwd)
                s.send_message(msg)
        else:
            with smtplib.SMTP(host, port) as s:
                if user: s.login(user, pwd)
                s.send_message(msg)
        return True

    raise RuntimeError(f"Unknown MAIL_BACKEND: {MAIL_BACKEND}")
