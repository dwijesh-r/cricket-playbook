#!/usr/bin/env python3
"""
StatSledge Chat API
===================
Lightweight FastAPI server wrapping Qwen3 (Ollama) + DuckDB.

Usage:
    uvicorn scripts.chatbot.api:app --port 8642 --reload

Or:
    python scripts/chatbot/api.py
"""

import json
import re
from pathlib import Path

import duckdb
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "cricket_playbook.duckdb"

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:8b"

app = FastAPI(title="StatSledge Chat API", version="1.0.0")

# Allow dashboard to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


# DuckDB connection (read-only, reconnect on each request for safety)
def get_db():
    return duckdb.connect(str(DB_PATH), read_only=True)


SCHEMA_CONTEXT = """
You are Richmond, StatSledge's IPL cricket analytics assistant (IPL 2026 pre-tournament analysis).
You answer questions by writing DuckDB SQL queries against the analytics database.

## IMPORTANT RULES
1. ONLY output a JSON object: {"sql": "YOUR QUERY", "explanation": "brief description"}
2. Use ONLY the tables and columns listed below. Do NOT invent tables or columns.
3. All data is IPL (Indian Premier League) from 2008-2025. IPL 2026 has NOT started.
4. Player names use format like 'V Kohli', 'SA Yadav', 'Shubman Gill', 'JC Buttler'.
   If the user says a full name like "Virat Kohli", search with: player_name ILIKE '%Kohli%'
5. Use ILIKE for all name matching (case-insensitive).
6. LIMIT results to 20 rows max unless the user asks for more.
7. Do NOT use CTEs or subqueries unless truly necessary. Keep queries simple.
8. Most tables have a sample_size column ('LOW', 'MEDIUM', 'HIGH'). When ranking or
   comparing players, ALWAYS filter to sample_size IN ('MEDIUM', 'HIGH') to avoid
   misleading results from small samples. Only include LOW sample if the user asks.
9. When the user asks for "best" or "top", order by the most relevant stat and LIMIT.

## AVAILABLE TABLES

### analytics_ipl_batting_career
Career batting stats for all IPL players (2023-2025).
Columns: player_id, player_name, primary_role, innings, runs, balls_faced,
  dismissals, highest_score, fifties, hundreds, fours, sixes, dot_balls,
  strike_rate, batting_average, boundary_pct, dot_ball_pct, sample_size

### analytics_ipl_bowling_career
Career bowling stats (2023-2025).
Columns: player_id, player_name, primary_role, matches_bowled, balls_bowled,
  overs_bowled, runs_conceded, wickets, best_wickets, best_runs, dot_balls,
  fours_conceded, sixes_conceded, economy_rate, bowling_average,
  bowling_strike_rate, dot_ball_pct, boundary_conceded_pct, sample_size

### analytics_ipl_batter_phase
Batting stats split by match phase.
Columns: player_id, player_name, match_phase, innings, runs, balls_faced,
  dismissals, fours, sixes, dot_balls, strike_rate, batting_average,
  boundary_pct, dot_ball_pct, sample_size
PHASE VALUES: 'powerplay' (overs 1-6), 'middle' (overs 7-15), 'death' (overs 16-20)

### analytics_ipl_bowler_phase
Bowling stats split by match phase.
Columns: player_id, player_name, match_phase, matches, balls_bowled, overs,
  runs_conceded, wickets, dot_balls, fours_conceded, sixes_conceded,
  economy_rate, bowling_average, dot_ball_pct, boundary_conceded_pct, sample_size

### analytics_ipl_batter_vs_bowler
Head-to-head batter vs bowler matchups.
Columns: batter_id, batter_name, bowler_id, bowler_name, balls, runs,
  dismissals, strike_rate, average, dot_balls, fours, sixes,
  dot_ball_pct, boundary_pct, sample_size

### analytics_ipl_batter_vs_bowler_type
Batter performance vs bowling types.
Columns: batter_id, batter_name, bowler_type, balls, runs, dismissals,
  strike_rate, average, dot_balls, fours, sixes, dot_ball_pct, boundary_pct, sample_size
BOWLER_TYPE VALUES: 'Fast', 'Fast-Medium', 'Off-spin', 'Leg-spin', 'LA Orthodox',
  'Wrist-spin', 'Medium', 'Medium-Fast', 'Unknown'

### analytics_ipl_batter_vs_team
Batter performance against each IPL team.
Columns: batter_id, batter_name, opposition, innings, balls, runs, dismissals,
  fours, sixes, dot_balls, strike_rate, average, dot_ball_pct, boundary_pct, sample_size

### analytics_ipl_bowler_vs_team
Bowler performance against each IPL team.
Columns: bowler_id, bowler_name, opposition, innings, balls_bowled, runs_conceded,
  wickets, dot_balls, fours_conceded, sixes_conceded, economy_rate,
  bowling_average, dot_ball_pct, boundary_conceded_pct, sample_size

### analytics_ipl_squad_batting
IPL 2026 squad batting stats.
Columns: player_id, player_name, team_name, role, nationality, price_cr,
  innings, runs, balls_faced, strike_rate, batting_average, boundary_pct,
  dot_ball_pct, fours, sixes, highest_score, fifties, sample_size

### analytics_ipl_squad_bowling
IPL 2026 squad bowling stats.
Columns: player_id, player_name, team_name, role, nationality, price_cr,
  matches_bowled, overs_bowled, runs_conceded, wickets, economy_rate,
  bowling_average, bowling_strike_rate, dot_ball_pct, boundary_conceded_pct, sample_size

### ipl_2026_squads
Full IPL 2026 squad roster (232 players).
Columns: team_name, player_name, player_id, nationality, age, role,
  bowling_arm, bowling_type, batting_hand, batter_classification,
  bowler_classification, is_captain, bowling_style

## IPL TEAMS & ABBREVIATIONS
CSK = Chennai Super Kings, DC = Delhi Capitals, GT = Gujarat Titans,
KKR = Kolkata Knight Riders, LSG = Lucknow Super Giants,
MI = Mumbai Indians, PBKS = Punjab Kings, RR = Rajasthan Royals,
RCB = Royal Challengers Bengaluru, SRH = Sunrisers Hyderabad
"""

ANSWER_SYSTEM = (
    "You are Richmond, StatSledge's IPL cricket analytics assistant. "
    "Given the user's question and query results, write a concise answer. "
    "Include key numbers. Be conversational but precise. "
    "ALL data is IPL 2023-2025 only — do not reference career totals or other formats. "
    "If comparing players, highlight standout differences. "
    "Do NOT show SQL, table names, or technical details. "
    "Do NOT use thinking tags or <think> blocks. "
    "Keep the answer under 100 words."
)


class ChatRequest(BaseModel):
    question: str
    history: list = []


class ChatResponse(BaseModel):
    answer: str
    sql: str | None = None
    rows: int = 0
    error: str | None = None


def call_ollama(messages: list) -> str:
    """Call Ollama API with thinking disabled for faster responses."""
    # Append /no_think to the last user message to disable Qwen3's thinking mode
    msgs = []
    for m in messages:
        msgs.append(dict(m))
    if msgs and msgs[-1]["role"] == "user":
        msgs[-1]["content"] = msgs[-1]["content"] + " /no_think"

    resp = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": msgs,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 1024},
        },
        timeout=180,
    )
    resp.raise_for_status()
    result = resp.json()["message"]["content"]
    # If content is empty but thinking exists, use thinking as fallback
    if not result.strip():
        thinking = resp.json()["message"].get("thinking", "")
        if thinking:
            result = thinking
    return result


def extract_sql(response: str) -> str | None:
    """Extract SQL from Qwen3's response."""
    response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
    try:
        json_match = re.search(r"\{[^{}]*\}", response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("sql")
    except json.JSONDecodeError:
        pass
    sql_match = re.search(r"```sql\s*(.*?)\s*```", response, re.DOTALL)
    if sql_match:
        return sql_match.group(1).strip()
    select_match = re.search(r"(SELECT\s+.*?;)", response, re.DOTALL | re.IGNORECASE)
    if select_match:
        return select_match.group(1).strip()
    return None


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Process a chat question: generate SQL, execute, format answer."""
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Empty question")

    # Build messages with history
    messages = [{"role": "system", "content": SCHEMA_CONTEXT}]
    for h in req.history[-10:]:
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
    messages.append({"role": "user", "content": question})

    # Generate SQL
    try:
        raw = call_ollama(messages)
    except Exception as e:
        return ChatResponse(
            answer="Sorry, the AI model is not responding. Please try again.", error=str(e)
        )

    sql = extract_sql(raw)
    if not sql:
        return ChatResponse(
            answer="I couldn't understand that question. Try asking about a specific player, team, or stat.",
            error="no_sql_generated",
        )

    # Execute against DuckDB
    conn = get_db()
    try:
        result = conn.execute(sql)
        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()
    except Exception as e:
        # Retry with error context
        messages.append({"role": "assistant", "content": raw})
        messages.append(
            {
                "role": "user",
                "content": f"That SQL failed: {str(e)[:300]}. Fix the query using only the listed tables/columns.",
            }
        )
        try:
            retry_raw = call_ollama(messages)
            retry_sql = extract_sql(retry_raw)
            if retry_sql:
                result = conn.execute(retry_sql)
                columns = [desc[0] for desc in result.description]
                rows = result.fetchall()
                sql = retry_sql
            else:
                conn.close()
                return ChatResponse(
                    answer="I had trouble querying that. Could you rephrase?", error=str(e)
                )
        except Exception as e2:
            conn.close()
            return ChatResponse(
                answer="I had trouble querying that. Could you rephrase?", error=str(e2)
            )
    finally:
        conn.close()

    if not rows:
        return ChatResponse(
            answer="No data found for that query. The player may not have IPL stats in 2023-2025.",
            sql=sql,
            rows=0,
        )

    # Format results into natural language
    result_text = " | ".join(columns) + "\n"
    for row in rows[:20]:
        result_text += " | ".join(str(v) if v is not None else "" for v in row) + "\n"

    try:
        answer_raw = call_ollama(
            [
                {"role": "system", "content": ANSWER_SYSTEM},
                {"role": "user", "content": f"Question: {question}\n\nData:\n{result_text}"},
            ]
        )
        answer = re.sub(r"<think>.*?</think>", "", answer_raw, flags=re.DOTALL).strip()
    except Exception:
        # Fallback: just show raw data
        answer = f"Found {len(rows)} results. Top result: {dict(zip(columns, rows[0]))}"

    return ChatResponse(answer=answer, sql=sql, rows=len(rows))


@app.get("/health")
async def health():
    """Health check."""
    try:
        conn = get_db()
        count = conn.execute("SELECT COUNT(*) FROM analytics_ipl_batting_career").fetchone()[0]
        conn.close()
        return {"status": "ok", "players": count, "model": MODEL}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8642)
