#!/usr/bin/env python3
"""
Mission Control — Board Data Sync
==================================
Reads all .mission-control/data/tickets/TKT-*.json files and syncs them
into the dashboard index.html by replacing the inline `const tickets = [...]`
JavaScript array.

Usage:
    python scripts/mission_control/generate_board_data.py

Author: Brock Purdy (Data Pipeline Owner)
Sprint: TKT-245+ — Infrastructure & Pipeline Hardening
"""

import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TICKETS_DIR = PROJECT_ROOT / ".mission-control" / "data" / "tickets"
DASHBOARD_HTML = PROJECT_ROOT / "scripts" / "mission_control" / "dashboard" / "index.html"

# ---------------------------------------------------------------------------
# State mapping: JSON state -> Dashboard state
# ---------------------------------------------------------------------------
STATE_MAP = {
    "DONE": "DONE",
    "BACKLOG": "READY",
    "READY": "READY",
    "IN_PROGRESS": "IN_PROGRESS",
    "IDEA": "IDEA",
    "VALIDATION": "VALIDATION",
    "DEFERRED": "DEFERRED",
}

# ---------------------------------------------------------------------------
# Effort mapping: JSON effort -> Dashboard effort (kebab-case lowercase)
# ---------------------------------------------------------------------------
EFFORT_MAP = {
    "marathon": "marathon",
    "Marathon": "marathon",
    "deep-work": "deep-work",
    "deep work": "deep-work",
    "Deep Work": "deep-work",
    "Deep-Work": "deep-work",
    "hustle": "hustle",
    "Hustle": "hustle",
    "quick-win": "quick-win",
    "Quick Win": "quick-win",
    "Quick-Win": "quick-win",
}

# Size -> effort fallback (when effort is missing but size is present)
SIZE_TO_EFFORT = {
    "XS": "quick-win",
    "S": "hustle",
    "M": "deep-work",
    "L": "marathon",
    "XL": "marathon",
}


def _escape_js_string(s: str) -> str:
    """Escape a Python string for embedding in a JS single-quoted string."""
    s = s.replace("\\", "\\\\")
    s = s.replace("'", "\\'")
    s = s.replace("\n", "\\n")
    s = s.replace("\r", "")
    return s


def _flatten_gate(gate_value):
    """
    Flatten a gate value to a simple string for the dashboard.

    JSON gates can be:
      - A plain string: "PASS", "APPROVED", "YES"
      - A dict with a 'status' field: {"status": "APPROVED", "reason": "..."}
      - A dict with sub-reviewer keys: {"andy_flower": "YES", "date": "..."}
    """
    if isinstance(gate_value, str):
        return gate_value
    if isinstance(gate_value, dict):
        # If it has a 'status' key, use that
        if "status" in gate_value:
            return gate_value["status"]
        # If it has reviewer sub-keys like andy_flower: YES, aggregate
        reviewer_verdicts = [
            v
            for k, v in gate_value.items()
            if k != "date" and isinstance(v, str) and v in ("YES", "NO", "PASS", "FAIL")
        ]
        if reviewer_verdicts:
            return "YES" if all(v in ("YES", "PASS") for v in reviewer_verdicts) else "NO"
        return "APPROVED"
    return str(gate_value)


def _js_value(value, indent_level=0):
    """
    Convert a Python value to a JavaScript literal string.

    Handles strings, numbers, booleans, None, lists, and dicts.
    """
    indent = " " * indent_level
    inner_indent = " " * (indent_level + 2)

    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return f"'{_escape_js_string(value)}'"
    if isinstance(value, list):
        if not value:
            return "[]"
        # Short arrays of strings/numbers on one line
        if all(isinstance(v, (str, int, float)) for v in value) and len(value) <= 6:
            items = ", ".join(_js_value(v) for v in value)
            return f"[{items}]"
        # Longer or complex arrays
        items = []
        for v in value:
            items.append(f"{inner_indent}{_js_value(v, indent_level + 2)}")
        return "[\n" + ",\n".join(items) + f"\n{indent}]"
    if isinstance(value, dict):
        if not value:
            return "{}"
        pairs = []
        for k, v in value.items():
            js_key = (
                k if re.match(r"^[a-zA-Z_$][a-zA-Z0-9_$]*$", k) else f"'{_escape_js_string(k)}'"
            )
            pairs.append(f"{js_key}: {_js_value(v, indent_level + 2)}")
        # Compact single-level dicts on one line if short enough
        one_line = "{ " + ", ".join(pairs) + " }"
        if len(one_line) < 120 and "\n" not in one_line:
            return one_line
        lines = []
        for p in pairs:
            lines.append(f"{inner_indent}{p}")
        return "{\n" + ",\n".join(lines) + f"\n{indent}}}"
    return repr(value)


def load_ticket(filepath: Path) -> dict:
    """Load and parse a single ticket JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def map_ticket(raw: dict) -> dict:
    """
    Map a ticket JSON object to the dashboard's expected JS object format.

    Dashboard fields (observed):
        id, title, state, priority, effort, assignee, epic, progress, tags,
        gates, parent, blockedBy, context, completedNote, founderReviewNote,
        documents, plan, collaborators, ticketType
    """
    ticket = {}

    # --- Core fields ---
    ticket["id"] = raw.get("id", "")
    ticket["title"] = raw.get("title", "")

    # State mapping
    raw_state = raw.get("state", "BACKLOG")
    ticket["state"] = STATE_MAP.get(raw_state, raw_state)

    ticket["priority"] = raw.get("priority", "P2")

    # Effort: try effort field, then size fallback
    raw_effort = raw.get("effort", "")
    if raw_effort and raw_effort in EFFORT_MAP:
        ticket["effort"] = EFFORT_MAP[raw_effort]
    elif raw.get("size") and raw["size"] in SIZE_TO_EFFORT:
        ticket["effort"] = SIZE_TO_EFFORT[raw["size"]]
    else:
        ticket["effort"] = EFFORT_MAP.get(raw_effort, "deep-work")

    # Assignee: prefer assignee, fallback to owner
    ticket["assignee"] = raw.get("assignee") or raw.get("owner", "Unassigned")

    # Epic: prefer epic_id, fallback to epic
    ticket["epic"] = raw.get("epic_id") or raw.get("epic", "")

    # Progress
    ticket["progress"] = raw.get("progress_pct", 0)

    # Tags
    tags = raw.get("tags", [])
    # Add done tag for completed tickets
    if ticket["state"] == "DONE" and "✅ Done" not in tags:
        tags = tags + ["✅ Done"]
    ticket["tags"] = tags

    # --- Gates (flatten to simple key: value strings) ---
    raw_gates = raw.get("gates", {})
    if raw_gates:
        flat_gates = {}
        for gate_name, gate_val in raw_gates.items():
            flat_gates[gate_name] = _flatten_gate(gate_val)
        ticket["gates"] = flat_gates
    else:
        ticket["gates"] = {}

    # --- Optional relational fields ---
    if raw.get("parent"):
        ticket["parent"] = raw["parent"]

    if raw.get("blocked_by"):
        ticket["blockedBy"] = raw["blocked_by"]
    if raw.get("blocks"):
        ticket["blocks"] = raw["blocks"]

    # --- Optional metadata ---
    if raw.get("documents"):
        ticket["documents"] = raw["documents"]

    if raw.get("completedNote"):
        ticket["completedNote"] = raw["completedNote"]

    if raw.get("resolution_note"):
        ticket["completedNote"] = raw["resolution_note"]

    if raw.get("founderReviewNote"):
        ticket["founderReviewNote"] = raw["founderReviewNote"]

    if raw.get("collaborators"):
        ticket["collaborators"] = raw["collaborators"]

    if raw.get("deferred_reason"):
        ticket["deferredReason"] = raw["deferred_reason"]

    # --- Context from description (build a lightweight context object) ---
    desc = raw.get("description", "")
    if desc:
        ticket["context"] = {"ask": desc}

    return ticket


def ticket_sort_key(ticket: dict) -> int:
    """Extract numeric ID for sorting: TKT-001 -> 1."""
    m = re.search(r"TKT-(\d+)", ticket.get("id", ""))
    return int(m.group(1)) if m else 9999


def generate_tickets_js(tickets: list) -> str:
    """
    Generate the `const tickets = [...]` JavaScript block from a list
    of mapped ticket dicts.
    """
    lines = []
    lines.append("        const tickets = [")

    for i, tkt in enumerate(tickets):
        # Build the JS object for this ticket
        pairs = []
        # Ordered fields for readability
        field_order = [
            "id",
            "title",
            "state",
            "priority",
            "effort",
            "assignee",
            "epic",
            "progress",
            "tags",
            "gates",
            "parent",
            "blockedBy",
            "blocks",
            "context",
            "completedNote",
            "founderReviewNote",
            "documents",
            "collaborators",
            "deferredReason",
        ]
        for key in field_order:
            if key in tkt:
                val = tkt[key]
                js_key = key
                pairs.append(f"{js_key}: {_js_value(val, 14)}")

        # Include any extra keys not in field_order
        for key in tkt:
            if key not in field_order:
                pairs.append(f"{key}: {_js_value(tkt[key], 14)}")

        trailing = "," if i < len(tickets) - 1 else ""
        # Format: compact single-line if short enough, else multi-line
        one_line = "            { " + ", ".join(pairs) + " }" + trailing
        if len(one_line) <= 200:
            lines.append(one_line)
        else:
            lines.append("            {")
            for j, p in enumerate(pairs):
                sep = "," if j < len(pairs) - 1 else ""
                lines.append(f"              {p}{sep}")
            lines.append("            }" + trailing)

    lines.append("        ];")
    return "\n".join(lines)


def sync_dashboard(tickets_js: str) -> None:
    """
    Replace the existing `const tickets = [...]` block in index.html
    with the freshly generated JavaScript.
    """
    html = DASHBOARD_HTML.read_text(encoding="utf-8")

    # Pattern: match from `const tickets = [` to the closing `];`
    # The closing `];` is on its own line with 8 spaces of indentation
    pattern = re.compile(
        r"^(\s*const tickets = \[).*?^(\s*\];)",
        re.MULTILINE | re.DOTALL,
    )

    match = pattern.search(html)
    if not match:
        print("ERROR: Could not find 'const tickets = [...]' block in index.html")
        sys.exit(1)

    # Replace the matched block
    new_html = html[: match.start()] + tickets_js + html[match.end() :]

    DASHBOARD_HTML.write_text(new_html, encoding="utf-8")


def main():
    """Main entry point: load tickets, map, generate JS, sync dashboard."""
    # -----------------------------------------------------------------------
    # 1. Load all TKT-*.json files
    # -----------------------------------------------------------------------
    ticket_files = sorted(TICKETS_DIR.glob("TKT-*.json"))
    if not ticket_files:
        print(f"ERROR: No TKT-*.json files found in {TICKETS_DIR}")
        sys.exit(1)

    raw_tickets = []
    errors = []
    for tf in ticket_files:
        try:
            raw_tickets.append(load_ticket(tf))
        except (json.JSONDecodeError, OSError) as e:
            errors.append(f"  WARN: Skipping {tf.name}: {e}")

    if errors:
        for err in errors:
            print(err)

    print(f"Loaded {len(raw_tickets)} tickets from {TICKETS_DIR}")

    # -----------------------------------------------------------------------
    # 2. Map to dashboard format
    # -----------------------------------------------------------------------
    mapped = [map_ticket(t) for t in raw_tickets]
    mapped.sort(key=ticket_sort_key)

    # Stats
    states = {}
    for t in mapped:
        s = t["state"]
        states[s] = states.get(s, 0) + 1
    print(f"States: {states}")

    # -----------------------------------------------------------------------
    # 3. Generate JS
    # -----------------------------------------------------------------------
    tickets_js = generate_tickets_js(mapped)
    print(f"Generated {len(mapped)} ticket entries ({len(tickets_js)} chars)")

    # -----------------------------------------------------------------------
    # 4. Sync to dashboard
    # -----------------------------------------------------------------------
    sync_dashboard(tickets_js)
    print(f"Synced to {DASHBOARD_HTML}")

    # -----------------------------------------------------------------------
    # 5. Verify TKT-245
    # -----------------------------------------------------------------------
    tkt245 = [t for t in mapped if t["id"] == "TKT-245"]
    if tkt245:
        print(f"TKT-245 state: {tkt245[0]['state']} | progress: {tkt245[0]['progress']}")
    else:
        print("WARN: TKT-245 not found in ticket data")


if __name__ == "__main__":
    main()
