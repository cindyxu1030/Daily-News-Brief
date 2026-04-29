#!/usr/bin/env bash
# News Brief runner — called by the macOS LaunchAgent at 7am PST daily.
# Uses Sonnet 4.6 for cost-efficient research.

set -euo pipefail

export PATH="/Users/cindy/.local/bin:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"

ENV_FILE="$HOME/.config/news-brief/.env"
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

LOG_DIR="$HOME/.config/news-brief/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/newsbrief.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] News Brief starting..." >> "$LOG_FILE"

claude \
    --model claude-sonnet-4-6 \
    -p "Run news brief" \
    >> "$LOG_FILE" 2>&1

EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] News Brief completed." >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] News Brief FAILED (exit $EXIT_CODE)." >> "$LOG_FILE"
fi

exit $EXIT_CODE
