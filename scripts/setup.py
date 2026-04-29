#!/usr/bin/env python3
"""
News Brief one-time setup wizard.
Configures Gmail SMTP credentials and creates required directories.
Run once before using the skill: python3 setup.py
"""

import getpass
import smtplib
import ssl
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "news-brief"
ENV_FILE = CONFIG_DIR / ".env"
OUTPUT_DIR = Path.home() / "Documents" / "NewsBrief"
LOG_DIR = CONFIG_DIR / "logs"


def setup_directories():
    for d in (CONFIG_DIR, LOG_DIR, OUTPUT_DIR):
        d.mkdir(parents=True, exist_ok=True)
    print(f"  {CONFIG_DIR}")
    print(f"  {OUTPUT_DIR}")
    print(f"  {LOG_DIR}")


def get_credentials():
    print()
    print("--- Gmail SMTP Setup ---")
    print("You need a Gmail App Password (not your account password).")
    print("Generate at: myaccount.google.com -> Security -> 2-Step Verification -> App passwords")
    print()
    smtp_user = input("Gmail address (sender): ").strip()
    if not smtp_user:
        print("ERROR: Email cannot be empty.", file=sys.stderr)
        sys.exit(1)
    smtp_pass = getpass.getpass("App Password (hidden): ").strip()
    if not smtp_pass:
        print("ERROR: App Password cannot be empty.", file=sys.stderr)
        sys.exit(1)
    return smtp_user, smtp_pass


def test_credentials(smtp_user, smtp_pass):
    print()
    print("Testing credentials...", end=" ", flush=True)
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as s:
            s.login(smtp_user, smtp_pass)
        print("OK")
        return True
    except smtplib.SMTPAuthenticationError:
        print("FAILED")
        print("Auth failed. Use a 16-char App Password, not your account password.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        return False


def write_env(smtp_user, smtp_pass):
    content = (
        "# News Brief SMTP credentials - DO NOT commit this file\n"
        f"NEWSBRIEF_SMTP_USER={smtp_user}\n"
        f"NEWSBRIEF_SMTP_PASS={smtp_pass}\n"
        "NEWSBRIEF_SMTP_HOST=smtp.gmail.com\n"
        "NEWSBRIEF_SMTP_PORT=465\n"
    )
    ENV_FILE.write_text(content, encoding="utf-8")
    ENV_FILE.chmod(0o600)
    print(f"  Saved to {ENV_FILE} (mode 600)")


def main():
    print("=== News Brief Setup ===")
    print()
    print("1. Creating directories...")
    setup_directories()

    smtp_user, smtp_pass = get_credentials()

    if not test_credentials(smtp_user, smtp_pass):
        print("Setup aborted. Fix credentials and re-run.", file=sys.stderr)
        sys.exit(1)

    print()
    print("2. Saving credentials...")
    write_env(smtp_user, smtp_pass)

    print()
    print("Setup complete.")
    print()
    print("Next steps:")
    print("  1. Load the LaunchAgent (daily 7am PST trigger):")
    print("     launchctl load ~/Library/LaunchAgents/com.cindyspark.newsbrief.plist")
    print()
    print("  2. Test manually:")
    print('     claude --model claude-sonnet-4-6 -p "Run news brief"')
    print()
    print(f"  Archive saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
