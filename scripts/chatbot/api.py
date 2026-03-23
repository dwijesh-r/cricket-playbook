#!/usr/bin/env python3
"""
StatSledge Chat API
===================
FastAPI server wrapping Groq LLM API + DuckDB for the Richmond chatbot.

Usage:
    uvicorn scripts.chatbot.api:app --port 8642 --reload

Or:
    python scripts/chatbot/api.py

Requires:
    GROQ_API_KEY environment variable (free at console.groq.com)
"""

import json
import os
import re
from pathlib import Path

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "cricket_playbook.duckdb"

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Database mode: "neon" (production) or "duckdb" (local)
DB_MODE = os.environ.get("DB_MODE", "duckdb")

app = FastAPI(title="StatSledge Chat API", version="1.0.0")

# Allow dashboard to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


def run_query(sql: str) -> tuple[list[str], list[tuple]]:
    """Execute SQL and return (columns, rows). Works with both DuckDB and Neon."""
    if DB_MODE == "neon":
        import psycopg2

        url = os.environ.get("NEON_DATABASE_URL", "")
        conn = psycopg2.connect(url)
        try:
            cur = conn.cursor()
            cur.execute(sql)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return columns, rows
        finally:
            conn.close()
    else:
        import duckdb

        conn = duckdb.connect(str(DB_PATH), read_only=True)
        try:
            result = conn.execute(sql)
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()
            return columns, rows
        finally:
            conn.close()


SCHEMA_CONTEXT = """
You are Richmond, StatSledge's IPL cricket analytics assistant.
You help fans, analysts, and fantasy players explore IPL data (2023-2025, 219 matches).
You answer questions by writing DuckDB SQL queries against the analytics database.

## PERSONALITY
- Confident, knowledgeable cricket analyst. Think Harsha Bhogle meets data scientist.
- Give context with numbers. Don't just list stats, interpret them.
- If a question is casual ("hi", "hello"), respond warmly without SQL: {"sql": null, "explanation": "greeting"}
- If a question is about predictions or opinions, give a thoughtful take based on data, no SQL needed.

## RULES
1. Output a JSON object: {"sql": "YOUR QUERY", "explanation": "brief description"}
2. If no SQL is needed (greetings, opinions, explanations), use: {"sql": null, "explanation": "your response"}
3. Use ONLY the tables and columns listed below.
4. Player names use Cricsheet format: 'V Kohli', 'SA Yadav', 'JC Buttler'.
   ALWAYS use ILIKE '%LastName%' for matching. Common mappings:
   Virat Kohli → '%Kohli%', Rohit Sharma → '%Sharma%' (careful, many Sharmas — use '%RG Sharma%' or '%Rohit%'),
   MS Dhoni → '%Dhoni%', Bumrah → '%Bumrah%', Hardik Pandya → '%Pandya%' (use '%HH Pandya%'),
   Rishabh Pant → '%Pant%', Suryakumar → '%SA Yadav%', KL Rahul → '%KL Rahul%'
5. LIMIT to 10 rows for rankings, 20 for lists.
6. Filter sample_size IN ('MEDIUM', 'HIGH') for rankings. Include LOW only if asked.
7. Keep queries simple. No CTEs unless necessary.

## FEW-SHOT EXAMPLES

User: "How does Kohli perform in death overs?"
{"sql": "SELECT player_name, strike_rate, batting_average, runs, balls_faced, boundary_pct FROM analytics_ipl_batter_phase WHERE player_name ILIKE '%Kohli%' AND match_phase = 'death'", "explanation": "Kohli's death overs batting stats"}

User: "Top 5 wicket takers in powerplay"
{"sql": "SELECT player_name, wickets, economy_rate, overs, dot_ball_pct FROM analytics_ipl_bowler_phase WHERE match_phase = 'powerplay' AND sample_size IN ('MEDIUM', 'HIGH') ORDER BY wickets DESC LIMIT 5", "explanation": "Top powerplay wicket-takers with qualified sample"}

User: "Bumrah vs Kohli head to head"
{"sql": "SELECT batter_name, bowler_name, balls, runs, dismissals, strike_rate FROM analytics_ipl_batter_vs_bowler WHERE batter_name ILIKE '%Kohli%' AND bowler_name ILIKE '%Bumrah%'", "explanation": "Kohli vs Bumrah H2H matchup"}

User: "Which team has the most expensive squad?"
{"sql": "SELECT team_name, COUNT(*) as players, SUM(price_cr) as total_spend, ROUND(AVG(price_cr), 2) as avg_price FROM ipl_2026_squads GROUP BY team_name ORDER BY total_spend DESC", "explanation": "Squad spend by team"}

User: "Compare Jaiswal and Gill in powerplay"
{"sql": "SELECT player_name, strike_rate, batting_average, runs, balls_faced, boundary_pct, dot_ball_pct FROM analytics_ipl_batter_phase WHERE (player_name ILIKE '%Jaiswal%' OR player_name ILIKE '%Gill%') AND match_phase = 'powerplay' AND sample_size IN ('MEDIUM', 'HIGH')", "explanation": "Jaiswal vs Gill powerplay comparison"}

User: "CSK overseas players"
{"sql": "SELECT player_name, role, nationality, age, price_cr FROM ipl_2026_squads WHERE team_name = 'Chennai Super Kings' AND nationality != 'IND' ORDER BY price_cr DESC", "explanation": "CSK overseas contingent"}

User: "Who hits the most sixes?"
{"sql": "SELECT player_name, sixes, runs, strike_rate, innings FROM analytics_ipl_batting_career WHERE sample_size IN ('MEDIUM', 'HIGH') ORDER BY sixes DESC LIMIT 10", "explanation": "Top six-hitters since 2023"}

User: "Best death bowlers"
{"sql": "SELECT player_name, economy_rate, wickets, overs, dot_ball_pct, boundary_conceded_pct FROM analytics_ipl_bowler_phase WHERE match_phase = 'death' AND sample_size IN ('MEDIUM', 'HIGH') ORDER BY economy_rate ASC LIMIT 10", "explanation": "Most economical death bowlers"}

User: "hello"
{"sql": null, "explanation": "Hey! I'm Richmond, StatSledge's cricket analyst. I can look up any IPL stat from 2023-2025. Try asking about player matchups, phase stats, team squads, or head-to-head records."}

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
BOWLER_TYPE VALUES: 'Right-arm Pace', 'Left-arm Pace', 'Off-spin', 'Leg-spin',
  'LA Orthodox', 'Left-arm orthodox', 'Wrist-spin', 'Unknown'

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
    "Given the user's question and query results, write a clear, insightful answer. "
    "Rules: "
    "1. Lead with the key finding, then support with numbers. "
    "2. ALL data is IPL 2023-2025 (219 matches). Never say 'career' or reference other formats. "
    "3. If comparing players, highlight the meaningful difference, not just who has more. "
    "4. Add brief context: 'which is above the league average of X' or 'ranking him Nth overall'. "
    "5. End with a suggested follow-up question the user might find interesting. Format: 'Try asking: ...' "
    "6. Do NOT show SQL, table names, column names, or technical details. "
    "7. Do NOT use thinking tags, <think> blocks, or em dashes. "
    "8. Keep it under 120 words. Be conversational like Harsha Bhogle, not robotic."
)


class ChatRequest(BaseModel):
    question: str
    history: list = []


class TableData(BaseModel):
    columns: list[str] = []
    data: list[list] = []


class ChatResponse(BaseModel):
    answer: str
    sql: str | None = None
    rows: int = 0
    error: str | None = None
    table: TableData | None = None
    suggested: str | None = None


def get_groq_key() -> str:
    """Get Groq API key from environment or .env file."""
    key = os.environ.get("GROQ_API_KEY")
    if key:
        return key
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("GROQ_API_KEY="):
                    return line.split("=", 1)[1]
    raise RuntimeError("GROQ_API_KEY not set. Add it to .env or export it.")


def call_llm(messages: list) -> str:
    """Call Groq API for fast LLM inference."""
    resp = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {get_groq_key()}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ_MODEL,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 1024,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


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
        raw = call_llm(messages)
    except Exception as e:
        return ChatResponse(
            answer="Sorry, the AI model is not responding. Please try again.", error=str(e)
        )

    sql = extract_sql(raw)

    # Handle non-SQL responses (greetings, opinions, explanations)
    if not sql:
        # Check if the LLM gave an explanation instead of SQL
        try:
            json_match = re.search(r"\{[^{}]*\}", raw, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                explanation = data.get("explanation", "")
                if explanation and data.get("sql") is None:
                    return ChatResponse(answer=explanation, sql=None, rows=0)
        except (json.JSONDecodeError, AttributeError):
            pass
        return ChatResponse(
            answer="I'm not sure how to answer that one. Try asking about a specific player, team, or IPL stat. For example: 'Top 5 run scorers since 2023' or 'How does Bumrah bowl in the death overs?'",
            error="no_sql_generated",
        )

    # Execute against database
    try:
        columns, rows = run_query(sql)
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
            retry_raw = call_llm(messages)
            retry_sql = extract_sql(retry_raw)
            if retry_sql:
                columns, rows = run_query(retry_sql)
                sql = retry_sql
            else:
                return ChatResponse(
                    answer="I had trouble querying that. Could you rephrase?", error=str(e)
                )
        except Exception as e2:
            return ChatResponse(
                answer="I had trouble querying that. Could you rephrase?", error=str(e2)
            )

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
        answer_raw = call_llm(
            [
                {"role": "system", "content": ANSWER_SYSTEM},
                {"role": "user", "content": f"Question: {question}\n\nData:\n{result_text}"},
            ]
        )
        answer = re.sub(r"<think>.*?</think>", "", answer_raw, flags=re.DOTALL).strip()
    except Exception:
        # Fallback: just show raw data
        answer = f"Found {len(rows)} results. Top result: {dict(zip(columns, rows[0]))}"

    # Build table data for frontend
    table = TableData(
        columns=columns, data=[[str(v) if v is not None else "" for v in row] for row in rows[:20]]
    )

    # Extract suggested follow-up from answer if present
    suggested = None
    if "Try asking:" in answer:
        parts = answer.split("Try asking:")
        answer = parts[0].strip()
        suggested = parts[1].strip().strip('"').strip("'")

    return ChatResponse(answer=answer, sql=sql, rows=len(rows), table=table, suggested=suggested)


@app.get("/health")
async def health():
    """Health check."""
    try:
        _, rows = run_query("SELECT COUNT(*) FROM analytics_ipl_batting_career")
        count = rows[0][0]
        return {"status": "ok", "players": count, "model": GROQ_MODEL, "db": DB_MODE}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8642)
