#!/usr/bin/env python3
"""
Generate season_previews.js from markdown source files.

Reads each team's markdown preview from outputs/season_previews/{TEAM}_season_preview.md,
parses the content into structured JS objects, and writes the full season_previews.js file.

Preserves existing top-level fields (meta, headline, verdict, byTheNumbers, categoryRatings,
keysToVictory, scoutingReport) from the current JS file via Node.js extraction.
Generates sections[] and boldTake from the markdown source for ALL teams.

Usage:
    python scripts/the_lab/generate_season_previews.py
"""

import json
import os
import re
import subprocess
import sys

# Team codes mapping to markdown filenames
TEAMS = ["RCB", "MI", "CSK", "KKR", "DC", "PBKS", "RR", "SRH", "GT", "LSG"]

# Sections that are already represented in top-level JS fields
# and should NOT appear in the sections[] array
SKIP_SECTIONS = {
    "the headline",
    "the verdict",
    "verdict",
    "by the numbers",
    "category ratings",
    "keys to victory",
    "andy flower's scouting report",
    "andy flowers scouting report",
}

# Section title -> id mapping
SECTION_ID_MAP = {
    "the story": "story",
    "off-season changes": "offseason",
    "auction strategy": "auctionStrategy",
    "full squad table": "squad",
    "full squad": "squad",
    "team style analysis": "teamStyle",
    "team batting profile": "battingProfile",
    "innings context": "inningsContext",
    "venue analysis": "venue",
    "schedule analysis": "schedule",
    "head-to-head record": "headToHead",
    "players to watch": "playersToWatch",
    "players who need to step up": "playersStepUp",
    "recent form": "recentForm",
    "momentum": "momentum",
    "tactical blueprint": "tactical",
    "interesting data insights": "dataInsights",
    "early season scenarios": "earlyScenarios",
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PREVIEWS_DIR = os.path.join(BASE_DIR, "outputs", "season_previews")
OUTPUT_FILE = os.path.join(
    BASE_DIR, "scripts", "the_lab", "dashboard", "data", "season_previews.js"
)


def replace_em_dashes(text: str) -> str:
    """Replace em dashes with appropriate alternatives."""
    text = text.replace("\u2014", ", ")
    text = text.replace(" -- ", ", ")
    text = text.replace("--", ", ")
    text = text.replace("  ", " ")
    return text


def escape_js_string(s: str) -> str:
    """Escape a string for use in JavaScript single-quoted strings."""
    s = s.replace("\\", "\\\\")
    s = s.replace("'", "\\'")
    s = s.replace("\n", "\\n")
    s = s.replace("\r", "")
    return s


def md_inline_to_html(text: str) -> str:
    """Convert basic markdown inline formatting to HTML."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def parse_table(lines: list) -> dict:
    """Parse a markdown table into a table block."""
    if len(lines) < 2:
        return None
    header_line = lines[0].strip()
    headers = [h.strip() for h in header_line.strip("|").split("|")]
    headers = [md_inline_to_html(h) for h in headers]
    rows = []
    for line in lines[2:]:
        line = line.strip()
        if not line or not line.startswith("|"):
            break
        cells = [md_inline_to_html(c.strip()) for c in line.strip("|").split("|")]
        rows.append(cells)
    return {"type": "table", "headers": headers, "rows": rows}


def parse_section_content(content_lines: list) -> list:
    """Parse markdown content lines into an array of content blocks."""
    blocks = []
    i = 0

    while i < len(content_lines):
        line = content_lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped == "---":
            i += 1
            continue

        # Subheading
        if stripped.startswith("### "):
            text = stripped[4:].strip()
            text = md_inline_to_html(text)
            text = replace_em_dashes(text)
            blocks.append({"type": "subheading", "content": text})
            i += 1
            continue

        # Table
        if stripped.startswith("|"):
            table_lines = []
            while i < len(content_lines) and content_lines[i].strip().startswith("|"):
                table_lines.append(content_lines[i])
                i += 1
            table_block = parse_table(table_lines)
            if table_block:
                table_block["headers"] = [replace_em_dashes(h) for h in table_block["headers"]]
                table_block["rows"] = [
                    [replace_em_dashes(c) for c in row] for row in table_block["rows"]
                ]
                blocks.append(table_block)
            continue

        # Unordered list
        if stripped.startswith("- ") or stripped.startswith("* "):
            items = []
            while i < len(content_lines):
                s = content_lines[i].strip()
                if s.startswith("- ") or s.startswith("* "):
                    item_text = s[2:].strip()
                    item_text = md_inline_to_html(item_text)
                    item_text = replace_em_dashes(item_text)
                    items.append(item_text)
                    i += 1
                elif s and not s.startswith("#") and not s.startswith("|") and s != "---":
                    if items:
                        items[-1] += " " + md_inline_to_html(replace_em_dashes(s))
                    i += 1
                else:
                    break
            if items:
                blocks.append({"type": "list", "items": items})
            continue

        # Ordered list
        if re.match(r"^\d+\.\s", stripped):
            items = []
            while i < len(content_lines):
                s = content_lines[i].strip()
                m = re.match(r"^\d+\.\s+(.*)", s)
                if m:
                    item_text = m.group(1).strip()
                    item_text = md_inline_to_html(item_text)
                    item_text = replace_em_dashes(item_text)
                    items.append(item_text)
                    i += 1
                elif s and not s.startswith("#") and not s.startswith("|") and s != "---":
                    if items:
                        items[-1] += " " + md_inline_to_html(replace_em_dashes(s))
                    i += 1
                else:
                    break
            if items:
                blocks.append({"type": "list", "items": items})
            continue

        # Paragraph text
        para_lines = []
        while i < len(content_lines):
            s = content_lines[i].strip()
            if (
                not s
                or s.startswith("###")
                or s.startswith("|")
                or s.startswith("- ")
                or s.startswith("* ")
                or s == "---"
                or re.match(r"^\d+\.\s", s)
            ):
                break
            para_lines.append(s)
            i += 1

        if para_lines:
            para_text = " ".join(para_lines)
            para_text = md_inline_to_html(para_text)
            para_text = replace_em_dashes(para_text)
            blocks.append({"type": "text", "content": f"<p>{para_text}</p>"})

    return blocks


def get_section_id(title: str) -> str:
    """Generate a section ID from the title."""
    normalized = title.lower().strip()
    for key, sid in SECTION_ID_MAP.items():
        if normalized.startswith(key) or key in normalized:
            return sid
    words = re.findall(r"[a-zA-Z]+", title)
    if not words:
        return "section"
    result = words[0].lower()
    for w in words[1:]:
        result += w.capitalize()
    return result


def should_skip_section(title: str) -> bool:
    """Check if this section should be skipped."""
    normalized = title.lower().strip()
    for skip in SKIP_SECTIONS:
        if normalized == skip or normalized.startswith(skip):
            return True
    return False


def is_bold_take_section(title: str) -> bool:
    """Check if this section is the Bold Take."""
    normalized = title.lower().strip()
    return normalized in ("bold take", "the bold take")


def parse_bold_take(content_lines: list) -> dict:
    """Parse bold take section into claim + argument."""
    claim = ""
    argument_lines = []
    found_claim = False

    for line in content_lines:
        stripped = line.strip()
        if not stripped or stripped == "---":
            continue

        if not found_claim:
            m = re.match(r"^\*\*(.+?)\*\*\.?$", stripped)
            if m:
                claim = m.group(1).strip().rstrip(".")
                found_claim = True
                continue
            if stripped:
                claim = stripped.strip("*").strip()
                found_claim = True
                continue
        else:
            argument_lines.append(stripped)

    argument = " ".join(argument_lines)
    argument = md_inline_to_html(argument)
    argument = replace_em_dashes(argument)
    claim = replace_em_dashes(claim)

    return {"claim": claim, "argument": argument}


def parse_markdown(filepath: str) -> dict:
    """Parse a team's markdown preview file into structured data."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    sections_raw = []
    current_title = None
    current_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## ") and not stripped.startswith("### "):
            if current_title is not None:
                sections_raw.append((current_title, current_lines))
            current_title = stripped[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_title is not None:
        sections_raw.append((current_title, current_lines))

    result = {
        "boldTake": None,
        "sections": [],
    }

    for title, content in sections_raw:
        # Bold Take
        if is_bold_take_section(title):
            result["boldTake"] = parse_bold_take(content)
            continue

        # Skip sections already in top-level JS
        if should_skip_section(title):
            continue

        # Headline and Verdict are also skip candidates
        if title.lower().strip() == "the headline":
            continue
        if title.lower().strip() in ("the verdict", "verdict"):
            continue

        display_title = title.strip()
        section_id = get_section_id(display_title)
        blocks = parse_section_content(content)

        if blocks:
            summary = ""
            for b in blocks:
                if b["type"] == "text":
                    raw = re.sub(r"<[^>]+>", "", b["content"])
                    if len(raw) > 200:
                        summary = raw[:197] + "..."
                    else:
                        summary = raw
                    break

            section_obj = {
                "id": section_id,
                "title": replace_em_dashes(display_title),
                "summary": replace_em_dashes(summary),
                "blocks": blocks,
            }
            result["sections"].append(section_obj)

    return result


def extract_existing_data_via_node(js_path: str) -> dict:
    """Use Node.js to parse the existing JS file and extract team data as JSON."""
    node_script = f"""
    const fs = require('fs');
    let content = fs.readFileSync('{js_path}', 'utf-8');
    // Replace const with var so eval puts it in scope
    content = content.replace('const SEASON_PREVIEWS', 'var SEASON_PREVIEWS');
    eval(content);
    // For each team, extract everything except sections and boldTake
    const result = {{}};
    for (const [team, data] of Object.entries(SEASON_PREVIEWS)) {{
        const {{ sections, boldTake, ...rest }} = data;
        result[team] = rest;
    }}
    console.log(JSON.stringify(result));
    """
    proc = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        print(f"Node.js error: {proc.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(proc.stdout)


def write_js_block(value, indent=2):
    """Write a Python value as formatted JS source."""
    pad = "  " * indent

    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        # Preserve float formatting
        if isinstance(value, float) and value == int(value):
            return str(int(value))
        return str(value)
    elif isinstance(value, str):
        return f"'{escape_js_string(value)}'"
    elif isinstance(value, list):
        if not value:
            return "[]"
        # Check if all items are simple (strings, numbers)
        all_simple = all(isinstance(v, (str, int, float, bool)) for v in value)
        if all_simple and len(value) <= 4:
            items = ", ".join(write_js_block(v, indent) for v in value)
            if len(items) < 100:
                return f"[{items}]"
        parts = []
        for v in value:
            parts.append(f"{pad}  {write_js_block(v, indent + 1)}")
        return "[\n" + ",\n".join(parts) + f"\n{pad}]"
    elif isinstance(value, dict):
        if not value:
            return "{}"
        # Check if dict is short enough for single line
        all_simple = all(isinstance(v, (str, int, float, bool)) for v in value.values())
        if all_simple and len(value) <= 3:
            items = ", ".join(f"{k}: {write_js_block(v, indent)}" for k, v in value.items())
            if len(items) < 120:
                return f"{{ {items} }}"
        parts = []
        for k, v in value.items():
            parts.append(f"{pad}  {k}: {write_js_block(v, indent + 1)}")
        return "{\n" + ",\n".join(parts) + f"\n{pad}}}"
    return str(value)


def write_blocks_js(blocks: list, indent: int) -> list:
    """Write content blocks as JS source lines."""
    pad = "  " * indent
    lines = []

    for bi, block in enumerate(blocks):
        comma = "," if bi < len(blocks) - 1 else ""
        btype = block["type"]

        if btype == "text":
            lines.append(
                f"{pad}{{ type: 'text', content: '{escape_js_string(block['content'])}' }}{comma}"
            )
        elif btype == "subheading":
            lines.append(
                f"{pad}{{ type: 'subheading', content: '{escape_js_string(block['content'])}' }}{comma}"
            )
        elif btype == "callout":
            lines.append(
                f"{pad}{{ type: 'callout', content: '{escape_js_string(block['content'])}' }}{comma}"
            )
        elif btype == "list":
            items_js = (
                "[" + ", ".join(f"'{escape_js_string(item)}'" for item in block["items"]) + "]"
            )
            lines.append(f"{pad}{{ type: 'list', items: {items_js} }}{comma}")
        elif btype == "table":
            headers_js = "[" + ", ".join(f"'{escape_js_string(h)}'" for h in block["headers"]) + "]"
            lines.append(f"{pad}{{")
            lines.append(f"{pad}  type: 'table',")
            lines.append(f"{pad}  headers: {headers_js},")
            lines.append(f"{pad}  rows: [")
            for ri, row in enumerate(block["rows"]):
                row_js = "[" + ", ".join(f"'{escape_js_string(c)}'" for c in row) + "]"
                row_comma = "," if ri < len(block["rows"]) - 1 else ""
                lines.append(f"{pad}    {row_js}{row_comma}")
            lines.append(f"{pad}  ]")
            lines.append(f"{pad}}}{comma}")

    return lines


def generate_full_js(existing_data: dict, markdown_data: dict) -> str:
    """Generate the complete season_previews.js file."""
    lines = [
        "/**",
        " * Season Previews Data",
        " * Cricket Playbook v5.0.0",
        " * Generated from outputs/season_previews/",
        " */",
        "",
        "const SEASON_PREVIEWS = {",
    ]

    team_keys = list(existing_data.keys())

    for ti, team in enumerate(team_keys):
        team_data = existing_data[team]
        md = markdown_data.get(team, {})
        team_comma = "," if ti < len(team_keys) - 1 else ""

        lines.append(f"  {team}: {{")
        lines.append("    available: true,")

        # meta
        if "meta" in team_data:
            lines.append(f"    meta: {write_js_block(team_data['meta'], 2)},")

        # headline
        if "headline" in team_data:
            lines.append(f"    headline: {write_js_block(team_data['headline'], 2)},")

        # verdict
        if "verdict" in team_data:
            lines.append(f"    verdict: {write_js_block(team_data['verdict'], 2)},")

        # byTheNumbers
        if "byTheNumbers" in team_data:
            lines.append("    byTheNumbers: [")
            for ni, item in enumerate(team_data["byTheNumbers"]):
                comma = "," if ni < len(team_data["byTheNumbers"]) - 1 else ""
                lines.append(f"      {write_js_block(item, 3)}{comma}")
            lines.append("    ],")

        # categoryRatings
        if "categoryRatings" in team_data:
            lines.append("    categoryRatings: [")
            for ni, item in enumerate(team_data["categoryRatings"]):
                comma = "," if ni < len(team_data["categoryRatings"]) - 1 else ""
                lines.append(f"      {write_js_block(item, 3)}{comma}")
            lines.append("    ],")

        # boldTake (from markdown)
        if md.get("boldTake"):
            bt = md["boldTake"]
            lines.append("    boldTake: {")
            lines.append(f"      claim: '{escape_js_string(bt['claim'])}',")
            lines.append(f"      argument: '{escape_js_string(bt['argument'])}'")
            lines.append("    },")

        # keysToVictory
        if "keysToVictory" in team_data:
            lines.append("    keysToVictory: [")
            for ni, item in enumerate(team_data["keysToVictory"]):
                comma = "," if ni < len(team_data["keysToVictory"]) - 1 else ""
                lines.append(f"      {write_js_block(item, 3)}{comma}")
            lines.append("    ],")

        # scoutingReport
        if "scoutingReport" in team_data:
            lines.append(f"    scoutingReport: {write_js_block(team_data['scoutingReport'], 2)},")

        # sections (from markdown)
        if md.get("sections"):
            lines.append("    sections: [")
            for si, section in enumerate(md["sections"]):
                section_comma = "," if si < len(md["sections"]) - 1 else ""
                lines.append("      {")
                lines.append(
                    f"        id: '{escape_js_string(section['id'])}',",
                )
                lines.append(
                    f"        title: '{escape_js_string(section['title'])}',",
                )
                lines.append(
                    f"        summary: '{escape_js_string(section['summary'])}',",
                )
                lines.append("        blocks: [")
                block_lines = write_blocks_js(section["blocks"], 5)
                lines.extend(block_lines)
                lines.append("        ]")
                lines.append(f"      }}{section_comma}")
            lines.append("    ]")

        lines.append(f"  }}{team_comma}")

    lines.append("};")
    lines.append("")

    return "\n".join(lines)


def main():
    # Parse all markdown files
    markdown_data = {}
    for team in TEAMS:
        md_path = os.path.join(PREVIEWS_DIR, f"{team}_season_preview.md")
        if not os.path.exists(md_path):
            md_path_sample = os.path.join(PREVIEWS_DIR, f"{team}_season_preview_sample.md")
            if os.path.exists(md_path_sample):
                md_path = md_path_sample
            else:
                print(f"WARNING: No markdown file found for {team}")
                continue

        print(f"Parsing {team} from {os.path.basename(md_path)}...")
        parsed = parse_markdown(md_path)
        markdown_data[team] = parsed
        print(
            f"  -> {len(parsed['sections'])} sections, boldTake: {'yes' if parsed['boldTake'] else 'no'}"
        )

    # Extract existing data from JS via Node.js
    print("\nExtracting existing data via Node.js...")
    existing_data = extract_existing_data_via_node(OUTPUT_FILE)
    print(f"  -> {len(existing_data)} teams found in existing JS")

    # Generate the full JS file
    print("\nGenerating season_previews.js...")
    js_output = generate_full_js(existing_data, markdown_data)

    # Replace any remaining em dashes in the output
    js_output = js_output.replace(" \u2014 ", ", ")
    js_output = js_output.replace("\u2014", ", ")

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(js_output)

    print(f"Output written to {OUTPUT_FILE}")
    print(f"Total teams: {len(existing_data)}")

    # Summary
    print("\nSections per team:")
    for team in TEAMS:
        if team in markdown_data:
            n = len(markdown_data[team]["sections"])
            bt = "yes" if markdown_data[team].get("boldTake") else "no"
            print(f"  {team}: {n} sections, boldTake: {bt}")


if __name__ == "__main__":
    main()
