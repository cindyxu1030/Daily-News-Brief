# news-brief

Personal daily news brief skill for Claude Code. Searches the last 24 hours across 5 categories, dedupes against the past week, picks 6 stories spanning ≥3 categories, and emails a digest. Built as a personal reader — not a content pipeline.

**Default categories**: AI Core · AI × Marketing · Tech Macro · Geopolitics & Econ · Culture & Creator Economy

Runs on demand (`/news-brief`) or daily via LaunchAgent.

---

## Install

1. Clone into your Claude Code skills directory:
   ```bash
   git clone https://github.com/cindyxu1030/Daily-News-Brief.git ~/.claude/skills/news-brief
   ```
2. Run setup (Gmail SMTP credentials + directories):
   ```bash
   python3 ~/.claude/skills/news-brief/scripts/setup.py
   ```
   Needs a Gmail **App Password** (not account password) — generate at myaccount.google.com → Security → 2-Step Verification → App passwords.
3. (Optional) Load LaunchAgent for daily 7am PST run:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.cindyspark.newsbrief.plist
   ```

Trigger manually inside Claude Code: `/news-brief` or "run news brief".

---

## Personalize

This skill is meant for individuals who want a personalized news feed based on their interests. Customize in 4 places:

### 1. Recipient email + subject

`SKILL.md` Step 6 — replace the `--to` address(es) with your own. Multiple recipients: comma-separated.

### 2. Categories + sources

`SKILL.md` Step 2 — edit the 5-category table. Replace categories with your interests (e.g., Climate, Biotech, Sports, Local Politics). For each category, list the authoritative domains/publications you trust. The skill uses these to shape WebSearch queries.

If you want a different number of categories, also update:
- Step 4 variety rule (`span ≥3 of the 5`)
- Step 3 scoring axes if your categories need different weighting

### 3. Story count + selection rules

`SKILL.md` Step 4 — change "6 stories" to your preferred count. Adjust the wildcard slot count, recency cutoffs (default 48hr), and category-overuse cap (default: cap at 1 if category ran 3 days straight).

### 4. Email format + archive path

`SKILL.md` Step 5 — change the email body template (headers, sections, "Why it matters" line).
`SKILL.md` Step 8 — change archive path (default `~/Documents/NewsBrief/YYYY-MM-DD.md`).

### 5. Schedule (optional)

LaunchAgent plist controls cadence (default: daily 7am PST). Edit `~/Library/LaunchAgents/com.cindyspark.newsbrief.plist` `StartCalendarInterval` to change time, or remove plist for manual-only.

---

## What it does NOT do

- No persona voice, no script generation, no social-media output. Pure reading digest.
- No fabricated urgency. Slow news day → ships 4 stories with a "slow cycle" note instead of padding.
- No re-surfacing — strict 7-day dedup against `~/.config/news-brief/seen.json`.

---

## Files

- `SKILL.md` — skill definition + run flow
- `scripts/setup.py` — one-time SMTP setup wizard
- `scripts/send_email.py` — Gmail SMTP sender
- `scripts/run_brief.sh` — LaunchAgent entrypoint (invokes `claude -p "Run news brief"`)

State lives in `~/.config/news-brief/` (sources, seen-cache, category history, `.env` credentials). Archive in `~/Documents/NewsBrief/`.
