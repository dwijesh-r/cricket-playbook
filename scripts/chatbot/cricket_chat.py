#!/usr/bin/env python3
"""
StatSledge Cricket Chatbot
==========================
Text-to-SQL chatbot using Qwen3 (via Ollama) + DuckDB.

User asks a natural language question → Qwen3 generates SQL →
DuckDB executes → Qwen3 formats the answer.

Usage:
    python scripts/chatbot/cricket_chat.py

Requires:
    - Ollama running with qwen3:8b pulled
    - data/cricket_playbook.duckdb (run ingest.py + analytics_ipl.py first)
"""

import json
import re
import sys
from pathlib import Path

import duckdb
import requests

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "cricket_playbook.duckdb"

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:8b"

# Schema context for the LLM — tells it exactly what tables/columns exist
SCHEMA_CONTEXT = """
You are a cricket analytics assistant for StatSledge (IPL 2026 pre-tournament analysis).
You answer questions by writing DuckDB SQL queries against the analytics database.

## IMPORTANT RULES
1. ONLY output a JSON object: {"sql": "YOUR QUERY", "explanation": "brief description"}
2. Use ONLY the tables and columns listed below. Do NOT invent tables or columns.
3. All data is IPL (Indian Premier League) from 2008-2025. IPL 2026 has NOT started.
4. Player names use format like 'V Kohli', 'SA Yadav', 'Shubman Gill', 'JC Buttler'.
   If the user says "Virat Kohli", search with: player_name ILIKE '%Kohli%'
   If the user says "Bumrah", search with: player_name ILIKE '%Bumrah%'
5. Use ILIKE for all name matching (case-insensitive).
6. LIMIT results to 20 rows max unless the user asks for more.
7. Do NOT use CTEs or subqueries unless truly necessary. Keep queries simple.

## AVAILABLE TABLES

### analytics_ipl_batting_career
Career batting stats for all IPL players (2023-2025, 271 players).
Columns: player_id, player_name, primary_role, innings, runs, balls_faced,
  dismissals, highest_score, fifties, hundreds, fours, sixes, dot_balls,
  strike_rate, batting_average, boundary_pct, dot_ball_pct, sample_size

### analytics_ipl_bowling_career
Career bowling stats (2023-2025, 208 players).
Columns: player_id, player_name, primary_role, matches_bowled, balls_bowled,
  overs_bowled, runs_conceded, wickets, best_wickets, best_runs, dot_balls,
  fours_conceded, sixes_conceded, economy_rate, bowling_average,
  bowling_strike_rate, dot_ball_pct, boundary_conceded_pct, sample_size

### analytics_ipl_batter_phase
Batting stats split by match phase (1,543 rows).
Columns: player_id, player_name, match_phase, innings, runs, balls_faced,
  dismissals, fours, sixes, dot_balls, strike_rate, batting_average,
  boundary_pct, dot_ball_pct, sample_size
PHASE VALUES: 'powerplay', 'middle', 'death'
  - powerplay = overs 1-6
  - middle = overs 7-15
  - death = overs 16-20

### analytics_ipl_bowler_phase
Bowling stats split by match phase (1,428 rows).
Columns: player_id, player_name, match_phase, matches, balls_bowled, overs,
  runs_conceded, wickets, dot_balls, fours_conceded, sixes_conceded,
  economy_rate, bowling_average, dot_ball_pct, boundary_conceded_pct, sample_size

### analytics_ipl_batter_vs_bowler
Head-to-head batter vs bowler matchups (29,519 rows).
Columns: batter_id, batter_name, bowler_id, bowler_name, balls, runs,
  dismissals, strike_rate, average, dot_balls, fours, sixes,
  dot_ball_pct, boundary_pct, sample_size

### analytics_ipl_batter_vs_bowler_type
Batter performance vs bowling types (3,183 rows).
Columns: batter_id, batter_name, bowler_type, balls, runs, dismissals,
  strike_rate, average, dot_balls, fours, sixes, dot_ball_pct, boundary_pct, sample_size
BOWLER_TYPE VALUES: 'Fast', 'Fast-Medium', 'Off-spin', 'Leg-spin', 'LA Orthodox',
  'Wrist-spin', 'Medium', 'Medium-Fast', 'Unknown'

### analytics_ipl_batter_vs_team
Batter performance against each IPL team (4,283 rows).
Columns: batter_id, batter_name, opposition, innings, balls, runs, dismissals,
  fours, sixes, dot_balls, strike_rate, average, dot_ball_pct, boundary_pct, sample_size

### analytics_ipl_bowler_vs_team
Bowler performance against each IPL team.
Columns: bowler_id, bowler_name, opposition, innings, balls_bowled, runs_conceded,
  wickets, dot_balls, fours_conceded, sixes_conceded, economy_rate,
  bowling_average, dot_ball_pct, boundary_conceded_pct, sample_size

### analytics_ipl_squad_batting
IPL 2026 squad batting stats (149 players).
Columns: player_id, player_name, team_name, role, nationality, price_cr,
  innings, runs, balls_faced, strike_rate, batting_average, boundary_pct,
  dot_ball_pct, fours, sixes, highest_score, fifties, sample_size

### analytics_ipl_squad_bowling
IPL 2026 squad bowling stats (160 players).
Columns: player_id, player_name, team_name, role, nationality, price_cr,
  matches_bowled, overs_bowled, runs_conceded, wickets, economy_rate,
  bowling_average, bowling_strike_rate, dot_ball_pct,
  boundary_conceded_pct, sample_size

### ipl_2026_squads
Full IPL 2026 squad roster (232 players).
Columns: team_name, player_name, player_id, nationality, age, role,
  bowling_arm, bowling_type, batting_hand, batter_classification,
  bowler_classification, is_captain, bowling_style

## IPL TEAMS
Chennai Super Kings, Delhi Capitals, Gujarat Titans, Kolkata Knight Riders,
Lucknow Super Giants, Mumbai Indians, Punjab Kings, Rajasthan Royals,
Royal Challengers Bengaluru, Sunrisers Hyderabad

## TEAM ABBREVIATIONS (for matching)
CSK = Chennai Super Kings, DC = Delhi Capitals, GT = Gujarat Titans,
KKR = Kolkata Knight Riders, LSG = Lucknow Super Giants,
MI = Mumbai Indians, PBKS = Punjab Kings, RR = Rajasthan Royals,
RCB = Royal Challengers Bengaluru, SRH = Sunrisers Hyderabad
"""


def query_ollama(messages: list) -> str:
    """Send a chat request to Ollama and return the response."""
    # Append /no_think to disable Qwen3's thinking mode for faster responses
    msgs = [dict(m) for m in messages]
    if msgs and msgs[-1]["role"] == "user":
        msgs[-1]["content"] = msgs[-1]["content"] + " /no_think"

    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": msgs,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 512},
            },
            timeout=180,
        )
        resp.raise_for_status()
        result = resp.json()["message"]["content"]
        if not result.strip():
            result = resp.json()["message"].get("thinking", "")
        return result
    except requests.exceptions.ConnectionError:
        print("\nError: Cannot connect to Ollama. Is it running? (ollama serve)")
        sys.exit(1)
    except Exception as e:
        return f"Error calling Ollama: {e}"


def extract_sql(response: str) -> str | None:
    """Extract SQL from Qwen3's JSON response."""
    # Remove thinking tags if present
    response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()

    # Try to parse as JSON
    try:
        # Find JSON in the response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("sql")
    except json.JSONDecodeError:
        pass

    # Fallback: extract SQL from code block
    sql_match = re.search(r"```sql\s*(.*?)\s*```", response, re.DOTALL)
    if sql_match:
        return sql_match.group(1).strip()

    # Last resort: look for SELECT statement
    select_match = re.search(r"(SELECT\s+.*?;)", response, re.DOTALL | re.IGNORECASE)
    if select_match:
        return select_match.group(1).strip()

    return None


def format_results(question: str, sql: str, results: list, columns: list) -> str:
    """Use Qwen3 to format query results into a natural language answer."""
    if not results:
        return "No data found for that query."

    # Build a simple text table for the LLM
    result_text = " | ".join(columns) + "\n"
    result_text += "-" * len(result_text) + "\n"
    for row in results[:20]:
        result_text += " | ".join(str(v) for v in row) + "\n"

    messages = [
        {
            "role": "system",
            "content": (
                "You are a cricket analytics assistant. "
                "Given the user's question and SQL query results, "
                "write a concise, insightful answer. "
                "Include key numbers. Be conversational but precise. "
                "If comparing players, highlight the standout stats. "
                "Do NOT show SQL or technical details. "
                "Keep the answer under 150 words. "
                "Do NOT use thinking tags."
            ),
        },
        {
            "role": "user",
            "content": f"Question: {question}\n\nData:\n{result_text}",
        },
    ]

    return query_ollama(messages)


def run_chat():
    """Main chat loop."""
    print("=" * 60)
    print("  StatSledge Cricket Chatbot")
    print("  Powered by Qwen3 + DuckDB")
    print("=" * 60)
    print()
    print("Ask me anything about IPL cricket stats (2023-2025).")
    print("Examples:")
    print('  "How does Kohli perform in death overs?"')
    print('  "Top 5 wicket takers in powerplay"')
    print('  "Bumrah vs Kohli head to head"')
    print('  "Best strike rate against spin"')
    print('  "Compare RCB and CSK batting lineups"')
    print()
    print("Type 'quit' to exit.")
    print("-" * 60)

    # Connect to DuckDB
    conn = duckdb.connect(str(DB_PATH), read_only=True)

    # Conversation history for context
    messages = [
        {"role": "system", "content": SCHEMA_CONTEXT},
    ]

    while True:
        try:
            question = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        # Add user question
        messages.append({"role": "user", "content": question})

        # Get SQL from Qwen3
        print("\nThinking...", end="", flush=True)
        response = query_ollama(messages)
        print("\r           \r", end="", flush=True)

        sql = extract_sql(response)

        if not sql:
            print(
                f"\nStatSledge: I couldn't generate a query for that. "
                f"Could you rephrase?\n(Raw: {response[:200]})"
            )
            messages.pop()  # Remove failed question
            continue

        # Execute SQL against DuckDB
        try:
            result = conn.execute(sql)
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()
        except Exception as e:
            error_msg = str(e)
            print(f"\nQuery error: {error_msg[:200]}")
            # Let Qwen3 try to fix it
            messages.append(
                {
                    "role": "assistant",
                    "content": response,
                }
            )
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"That SQL failed with error: {error_msg[:300]}. "
                        f"Please fix the query. Remember the exact table and column names."
                    ),
                }
            )
            print("Retrying...", end="", flush=True)
            retry_response = query_ollama(messages)
            print("\r            \r", end="", flush=True)

            retry_sql = extract_sql(retry_response)
            if retry_sql:
                try:
                    result = conn.execute(retry_sql)
                    columns = [desc[0] for desc in result.description]
                    rows = result.fetchall()
                    sql = retry_sql
                except Exception as e2:
                    print(f"\nRetry also failed: {e2}")
                    # Clean up conversation
                    messages = messages[:-3]
                    continue
            else:
                print("\nCouldn't fix the query. Try rephrasing.")
                messages = messages[:-2]
                continue

        # Format results
        print("Formatting...", end="", flush=True)
        answer = format_results(question, sql, rows, columns)
        # Clean thinking tags from answer
        answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL).strip()
        print("\r             \r", end="", flush=True)

        print(f"\nStatSledge: {answer}")
        print(f"\n  [SQL: {sql[:120]}{'...' if len(sql) > 120 else ''}]")
        print(f"  [Rows: {len(rows)}]")

        # Keep conversation history manageable (last 10 exchanges)
        if len(messages) > 21:
            messages = [messages[0]] + messages[-20:]

    conn.close()


if __name__ == "__main__":
    run_chat()
