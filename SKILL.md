---
name: news-brief
description: Cindy's personal daily news brief. Use when the user types /news-brief, /brief, /NewsBrief, "run news brief", "run the news brief", or asks for "today's news", "morning news", "daily brief", "news digest", "AI news", or similar. Searches the last 24 hours across 5 categories (AI Core, AI × Marketing, Tech Macro, Geopolitics & Econ, Culture & Creator Economy), deduplicates against the last 7 days, selects 6 stories spanning ≥3 categories, and emails a reading digest to cindyxu.1030@gmail.com. This is a personal reading brief — NOT a content-generation pipeline. No persona voice, no script output, no HeyGen. Also runs automatically daily at 7am PST via LaunchAgent.
---

# News Brief — Personal Daily Reader

Purpose: a concise, non-repetitive, 6-story morning reading brief. Neutral tone. No persona. No script. No content pipeline.

---

## Run flow

### Step 1 — Load caches

Read these files (create empty if missing):

- `~/.config/news-brief/sources.json` — category registry (authoritative list of sources per category + search guidance)
- `~/.config/news-brief/seen.json` — rolling **7-day** dedup cache; array of `{url, headline_hash, date}`
- `~/.config/news-brief/category_history.json` — rolling **14-day** log of categories used per day; array of `{date, categories: []}`

### Step 2 — Search each category (WebSearch, last 24hr)

Run 2–3 targeted WebSearch queries per category. Use `sources.json` to shape search terms toward the listed authoritative domains. The 5 categories:

| Category | Scope |
|---|---|
| **AI Core** | Model releases, lab news, research (OpenAI, Anthropic, Google DeepMind, Meta AI, DeepSeek, MiniMax, Kimi/Moonshot, ByteDance, research papers) |
| **AI × Marketing** | Adtech/martech updates, agency AI moves (Marketing Brew, AdWeek, Marketing Week, HubSpot, Adobe, Salesforce, Search Engine Journal) |
| **Tech Macro** | Big tech earnings, chips, IPOs, platform policy (Stratechery, The Information, TechCrunch, The Verge, Bloomberg tech) |
| **Geopolitics & Econ** | Wars, oil, rates, US-China decoupling, regulation (Reuters, FT, Bloomberg, WSJ, Semafor, Axios) |
| **Culture & Creator Economy** | Algorithm shifts, creator economy, viral moments, platform policy (Platformer, Garbage Day, Link in Bio, Hung Up, The Verge creator coverage) |

### Step 3 — Score each candidate (0–10)

Scoring axes:
- **Recency** (weight 2×): last 6hr = 10 · 6–24hr = 8 · 24–48hr = 5 · >48hr = reject
- **Novelty**: exact match in `seen.json` = 0 · same topic new angle = 4–6 · fresh = 8–10
- **Relevance**: stands on its own as worth knowing = 10. No angle-forcing.
- **Discussion-worthiness**: surprising stat / hot take / contrarian data / high-stakes decision = 8–10 · routine = 3–5

Drop anything in `seen.json` unless it's a substantial update (new model release, new data, new development).

### Step 4 — Select 6 stories with variety rules

- **Must span ≥3 of the 5 categories.** If top 6 cluster in 1–2, demote the weakest duplicates and promote next-best from other categories.
- **Bias away from categories overused in last 3 days** — check `category_history.json`. If AI Core ran 3 days straight, cap it at 1 story today.
- **1 wildcard slot**: highest-novelty story regardless of category.
- **If fewer than 6 qualify**: deliver what you have + explicit "slow news cycle" note. Do NOT pad.

### Step 5 — Format email body

Write to `/tmp/newsbrief_body.txt`. Neutral reporting tone, no persona. Format:

```
6 stories for today — categories: [list].

━━━ [CATEGORY NAME] ━━━
1. [Headline]
   [Source] · [URL] · [X] hours ago
   Summary: 2–3 sentences. What happened + why it happened.
   Why it matters: 1 sentence. The actual stakes.

2. [Headline]
   ...

━━━ [NEXT CATEGORY] ━━━
3. [Headline]
   ...

━━━ WILDCARD ━━━
6. [Headline]
   ...

Skipped today: [e.g., "AI × Marketing — covered 3 days running"]
```

### Step 6 — Send email

```bash
python3 ~/.claude/skills/news-brief/scripts/send_email.py \
  --to "cindyxu.1030@gmail.com,jiayuaw3@uci.edu" \
  --subject "News Brief — YYYY-MM-DD" \
  --body-file /tmp/newsbrief_body.txt
```

If the script exits non-zero: print the body directly in the conversation and tell the user to run `python3 ~/.claude/skills/news-brief/scripts/setup.py` to configure Gmail credentials.

### Step 7 — Update caches

- Append today's 6 stories to `seen.json` as `{url, headline_hash, date}`. Expire entries older than 7 days.
- Append today's entry to `category_history.json` as `{date, categories: [list of categories actually used]}`. Expire entries older than 14 days.

### Step 8 — Archive

Save the same email body as markdown to `~/Documents/NewsBrief/YYYY-MM-DD.md`. Overwrite if re-run same day.

### Step 9 — Confirm

One-line confirmation to the user:

```
News Brief sent to cindyxu.1030@gmail.com, jiayuaw3@uci.edu — 6 stories, categories: [list]. Archive: ~/Documents/NewsBrief/YYYY-MM-DD.md
```

---

## Standing rules

- **No persona, no Cindy Spark voice.** Neutral reporting tone.
- **No script generation, no HeyGen, no CTAs.** This is a reader, not a content pipeline.
- **No fabricated urgency.** If the news cycle is slow, say so; ship 4 stories not 6.
- **Dedup is strict.** Never surface a story already in `seen.json` unless it has a real new development.
- **Cite source + URL for every story.** Non-negotiable.
- **"Why it matters" must be specific.** No "this is important because of general trends." Name the actual mechanism (who's affected, how much, by when).
- **Today's date = today.** Use the `currentDate` from system context. Don't include stories older than 48hr.

---

## Models

- When invoked via LaunchAgent (`run_brief.sh`): Sonnet 4.6 for cost efficiency.
- When invoked interactively: use the session's active model.
