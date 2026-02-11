#!/usr/bin/env python3
"""
Generate token usage data from Claude Code's stats-cache.json.

Reads real token usage data from ~/.claude/stats-cache.json and project-level
JSONL session files, then writes a JavaScript data file consumed by the
Mission Control dashboard's Token Audit tab.

Usage:
    python scripts/mission_control/generate_token_data.py

Output:
    scripts/mission_control/dashboard/data/token_usage.js

Safe to run multiple times (idempotent). Handles missing source files gracefully.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
STATS_CACHE = Path.home() / ".claude" / "stats-cache.json"
PROJECT_SESSIONS_DIR = Path.home() / ".claude" / "projects" / "-Users-dwijeshreddy"
OUTPUT_DIR = Path(__file__).resolve().parent / "dashboard" / "data"
OUTPUT_FILE = OUTPUT_DIR / "token_usage.js"

# ---------------------------------------------------------------------------
# Model display name mapping
# ---------------------------------------------------------------------------
MODEL_DISPLAY_NAMES: dict[str, str] = {
    "claude-opus-4-5-20251101": "Claude Opus 4.5",
    "claude-opus-4-5": "Claude Opus 4.5",
    "claude-opus-4-6": "Claude Opus 4.6",
    "claude-sonnet-4-5-20241022": "Claude Sonnet 4.5",
    "claude-sonnet-4-5": "Claude Sonnet 4.5",
    "claude-sonnet-4-0": "Claude Sonnet 4.0",
    "claude-haiku-4-5": "Claude Haiku 4.5",
    "claude-haiku-3-5-20241022": "Claude Haiku 3.5",
}


def _display_name(model_id: str) -> str:
    """Return a human-readable model name."""
    return MODEL_DISPLAY_NAMES.get(model_id, model_id)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------
def _fmt(n: int | float) -> str:
    """Format a number with K/M/B suffix for JS comments."""
    n = int(n)
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


# ---------------------------------------------------------------------------
# Project session counting
# ---------------------------------------------------------------------------
def _count_project_sessions() -> int:
    """Count JSONL session files in the project directory tree."""
    if not PROJECT_SESSIONS_DIR.is_dir():
        return 0
    count = 0
    for f in PROJECT_SESSIONS_DIR.rglob("*.jsonl"):
        # Each JSONL file represents a session or subagent session
        count += 1
    return count


# ---------------------------------------------------------------------------
# Git log daily activity (supplements stats-cache gaps)
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _git_daily_commits() -> dict[str, int]:
    """Return {date: commit_count} from git log for the repo."""
    try:
        result = subprocess.run(
            ["git", "log", "--format=%ad", "--date=format:%Y-%m-%d"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=10,
        )
        if result.returncode != 0:
            return {}
        counts: dict[str, int] = {}
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if line:
                counts[line] = counts.get(line, 0) + 1
        return counts
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {}


# ---------------------------------------------------------------------------
# Main generation logic
# ---------------------------------------------------------------------------
def generate() -> dict:
    """Read stats-cache.json and produce the TOKEN_DATA structure."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Default empty data if file is missing
    if not STATS_CACHE.is_file():
        print(f"[warn] {STATS_CACHE} not found -- generating placeholder data")
        return _empty_data(now)

    with open(STATS_CACHE, "r") as f:
        raw = json.load(f)

    # ------------------------------------------------------------------
    # Summary totals from modelUsage
    # ------------------------------------------------------------------
    model_usage: dict = raw.get("modelUsage", {})

    total_input = 0
    total_output = 0
    total_cache_read = 0
    total_cache_creation = 0
    by_model: dict[str, dict] = {}

    for model_id, usage in model_usage.items():
        inp = usage.get("inputTokens", 0)
        out = usage.get("outputTokens", 0)
        cr = usage.get("cacheReadInputTokens", 0)
        cc = usage.get("cacheCreationInputTokens", 0)

        total_input += inp
        total_output += out
        total_cache_read += cr
        total_cache_creation += cc

        display = _display_name(model_id)
        if display in by_model:
            by_model[display]["input"] += inp
            by_model[display]["output"] += out
            by_model[display]["cacheRead"] += cr
            by_model[display]["cacheCreation"] += cc
        else:
            by_model[display] = {
                "input": inp,
                "output": out,
                "cacheRead": cr,
                "cacheCreation": cc,
            }

    total_tokens = total_input + total_output + total_cache_read + total_cache_creation

    # ------------------------------------------------------------------
    # Daily activity  (merge dailyActivity + dailyModelTokens)
    # ------------------------------------------------------------------
    daily_activity: list[dict] = raw.get("dailyActivity", [])
    daily_model_tokens: list[dict] = raw.get("dailyModelTokens", [])

    # Build a lookup for model tokens by date
    tokens_by_date: dict[str, int] = {}
    for entry in daily_model_tokens:
        date = entry.get("date", "")
        day_total = sum(entry.get("tokensByModel", {}).values())
        tokens_by_date[date] = tokens_by_date.get(date, 0) + day_total

    # Dates already covered by stats-cache
    cache_dates: set[str] = set()

    daily: list[dict] = []
    for entry in daily_activity:
        date = entry.get("date", "")
        cache_dates.add(date)
        daily.append(
            {
                "date": date,
                "messages": entry.get("messageCount", 0),
                "sessions": entry.get("sessionCount", 0),
                "tools": entry.get("toolCallCount", 0),
                "tokens": tokens_by_date.get(date, 0),
                "source": "stats-cache",
            }
        )

    # Supplement with git log for dates not in stats-cache
    git_commits = _git_daily_commits()
    for date, commit_count in git_commits.items():
        if date not in cache_dates:
            daily.append(
                {
                    "date": date,
                    "messages": 0,
                    "sessions": 1,
                    "tools": 0,
                    "tokens": 0,
                    "commits": commit_count,
                    "source": "git-log",
                }
            )

    # Sort by date
    daily.sort(key=lambda d: d["date"])

    # ------------------------------------------------------------------
    # Derived metrics
    # ------------------------------------------------------------------
    total_sessions = raw.get("totalSessions", 0)
    total_messages = raw.get("totalMessages", 0)
    days_active = len(daily) if daily else 1
    avg_daily_tokens = total_tokens // days_active if days_active > 0 else 0

    # Project-level session count
    project_sessions = _count_project_sessions()

    # ------------------------------------------------------------------
    # Billing cycle estimate  (Claude Max plan -- no per-token charges)
    # ------------------------------------------------------------------
    today = datetime.now(timezone.utc)
    # Assume monthly billing cycle starting the 1st
    cycle_start = today.replace(day=1)
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    days_remaining = (next_month - today).days

    # First session date
    first_session = raw.get("firstSessionDate", "")

    return {
        "summary": {
            "totalTokens": total_tokens,
            "inputTokens": total_input,
            "outputTokens": total_output,
            "cacheReadTokens": total_cache_read,
            "cacheCreationTokens": total_cache_creation,
            "totalSessions": total_sessions,
            "projectSessions": project_sessions,
            "totalMessages": total_messages,
            "daysActive": days_active,
            "avgDailyTokens": avg_daily_tokens,
            "firstSession": first_session,
            "lastUpdated": now,
        },
        "byModel": by_model,
        "daily": daily,
        "billingEstimate": {
            "plan": "Claude Max",
            "cycleStart": cycle_start.strftime("%Y-%m-%d"),
            "cycleEnd": next_month.strftime("%Y-%m-%d"),
            "daysRemaining": days_remaining,
            "note": "Subscription plan - no per-token charges",
        },
    }


def _empty_data(now: str) -> dict:
    """Return a placeholder TOKEN_DATA when no source data is available."""
    return {
        "summary": {
            "totalTokens": 0,
            "inputTokens": 0,
            "outputTokens": 0,
            "cacheReadTokens": 0,
            "cacheCreationTokens": 0,
            "totalSessions": 0,
            "projectSessions": 0,
            "totalMessages": 0,
            "daysActive": 0,
            "avgDailyTokens": 0,
            "firstSession": "",
            "lastUpdated": now,
        },
        "byModel": {},
        "daily": [],
        "billingEstimate": {
            "plan": "Claude Max",
            "cycleStart": "",
            "cycleEnd": "",
            "daysRemaining": 0,
            "note": "No data available - run Claude Code to generate stats",
        },
    }


# ---------------------------------------------------------------------------
# JavaScript output
# ---------------------------------------------------------------------------
def write_js(data: dict) -> None:
    """Write the TOKEN_DATA variable to a .js file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    summary = data["summary"]
    by_model = data["byModel"]
    daily = data["daily"]
    billing = data["billingEstimate"]

    lines: list[str] = []
    lines.append("// Auto-generated from ~/.claude/stats-cache.json")
    lines.append(f"// Last updated: {summary['lastUpdated']}")
    lines.append(
        f"// Total tokens: {_fmt(summary['totalTokens'])}  |  Sessions: {summary['totalSessions']}  |  Messages: {summary['totalMessages']}"
    )
    lines.append("//")
    lines.append("// Regenerate:  python scripts/mission_control/generate_token_data.py")
    lines.append("")
    lines.append("const TOKEN_DATA = {")

    # --- summary ---
    lines.append("    summary: {")
    lines.append(
        f"        totalTokens: {summary['totalTokens']},          // {_fmt(summary['totalTokens'])}"
    )
    lines.append(
        f"        inputTokens: {summary['inputTokens']},          // {_fmt(summary['inputTokens'])}"
    )
    lines.append(
        f"        outputTokens: {summary['outputTokens']},         // {_fmt(summary['outputTokens'])}"
    )
    lines.append(
        f"        cacheReadTokens: {summary['cacheReadTokens']},   // {_fmt(summary['cacheReadTokens'])}"
    )
    lines.append(
        f"        cacheCreationTokens: {summary['cacheCreationTokens']}, // {_fmt(summary['cacheCreationTokens'])}"
    )
    lines.append(f"        totalSessions: {summary['totalSessions']},")
    lines.append(f"        projectSessions: {summary['projectSessions']},")
    lines.append(f"        totalMessages: {summary['totalMessages']},")
    lines.append(f"        daysActive: {summary['daysActive']},")
    lines.append(
        f"        avgDailyTokens: {summary['avgDailyTokens']},     // {_fmt(summary['avgDailyTokens'])}"
    )
    lines.append(f'        firstSession: "{summary["firstSession"]}",')
    lines.append(f'        lastUpdated: "{summary["lastUpdated"]}"')
    lines.append("    },")

    # --- byModel ---
    lines.append("    byModel: {")
    for model_name, usage in by_model.items():
        total_model = usage["input"] + usage["output"] + usage["cacheRead"] + usage["cacheCreation"]
        lines.append(
            f'        "{model_name}": {{ input: {usage["input"]}, output: {usage["output"]}, cacheRead: {usage["cacheRead"]}, cacheCreation: {usage["cacheCreation"]} }},  // {_fmt(total_model)} total'
        )
    lines.append("    },")

    # --- daily ---
    lines.append("    daily: [")
    for d in daily:
        commits_part = f", commits: {d['commits']}" if d.get("commits") else ""
        source_part = f', source: "{d["source"]}"' if d.get("source") else ""
        lines.append(
            f'        {{ date: "{d["date"]}", messages: {d["messages"]}, sessions: {d["sessions"]}, tools: {d["tools"]}, tokens: {d["tokens"]}{commits_part}{source_part} }},'
        )
    lines.append("    ],")

    # --- billingEstimate ---
    lines.append("    billingEstimate: {")
    lines.append(f'        plan: "{billing["plan"]}",')
    lines.append(f'        cycleStart: "{billing["cycleStart"]}",')
    lines.append(f'        cycleEnd: "{billing["cycleEnd"]}",')
    lines.append(f"        daysRemaining: {billing['daysRemaining']},")
    lines.append(f'        note: "{billing["note"]}"')
    lines.append("    }")

    lines.append("};")
    lines.append("")

    # --- formatTokens helper ---
    lines.append("// Helper: format large token counts for display")
    lines.append("function formatTokens(n) {")
    lines.append("    if (n >= 1e9) return (n / 1e9).toFixed(1) + 'B';")
    lines.append("    if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';")
    lines.append("    if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K';")
    lines.append("    return n.toString();")
    lines.append("}")
    lines.append("")
    lines.append("// Helper: format token count with commas")
    lines.append("function formatTokensComma(n) {")
    lines.append("    return n.toLocaleString();")
    lines.append("}")
    lines.append("")

    js_content = "\n".join(lines)
    OUTPUT_FILE.write_text(js_content)
    print(f"[ok] Wrote {OUTPUT_FILE}  ({len(js_content)} bytes)")
    print(
        f"     Total tokens: {_fmt(summary['totalTokens'])}  |  Models: {len(by_model)}  |  Days active: {summary['daysActive']}"
    )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
def main() -> int:
    data = generate()
    write_js(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
