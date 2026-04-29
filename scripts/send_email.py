#!/usr/bin/env python3
"""
News Brief — Email sender
Sends the daily news digest via Gmail SMTP.

Usage:
  python3 send_email.py --to "addr@example.com" \
                        --subject "Subject line" \
                        --body-file /tmp/newsbrief_body.txt

Credentials are read from ~/.config/news-brief/.env:
  NEWSBRIEF_SMTP_USER=you@gmail.com
  NEWSBRIEF_SMTP_PASS=your-app-password
"""

import argparse
import os
import smtplib
import ssl
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

ENV_FILE = Path.home() / ".config" / "news-brief" / ".env"

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def load_env(path: Path) -> dict:
    env = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, val = line.partition("=")
            env[key.strip()] = val.strip()
    return env


def send(smtp_user: str, smtp_pass: str, to: str, subject: str, body: str) -> None:
    recipients = [addr.strip() for addr in to.split(",") if addr.strip()]
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(body, "plain", "utf-8"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, recipients, msg.as_string())


def main():
    parser = argparse.ArgumentParser(description="News Brief email sender")
    parser.add_argument("--to", required=True, help="Recipient email address(es), comma-separated for multiple")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--body-file", required=True, help="Path to plain-text body file")
    args = parser.parse_args()

    env = load_env(ENV_FILE)
    smtp_user = env.get("NEWSBRIEF_SMTP_USER") or os.environ.get("NEWSBRIEF_SMTP_USER", "")
    smtp_pass = env.get("NEWSBRIEF_SMTP_PASS") or os.environ.get("NEWSBRIEF_SMTP_PASS", "")

    if not smtp_user or not smtp_pass:
        print(
            "ERROR: Gmail credentials not found.\n"
            "Run: python3 ~/.claude/skills/news-brief/scripts/setup.py",
            file=sys.stderr,
        )
        sys.exit(1)

    body_path = Path(args.body_file)
    if not body_path.exists():
        print(f"ERROR: Body file not found: {body_path}", file=sys.stderr)
        sys.exit(1)
    body = body_path.read_text(encoding="utf-8")

    try:
        send(smtp_user, smtp_pass, args.to, args.subject, body)
        print(f"Email sent to {args.to}")
    except smtplib.SMTPAuthenticationError:
        print(
            "ERROR: Gmail authentication failed.\n"
            "Check your App Password at: https://myaccount.google.com/apppasswords\n"
            f"Then update: {ENV_FILE}",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to send email: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
