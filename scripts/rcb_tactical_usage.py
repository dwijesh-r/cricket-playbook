#!/usr/bin/env python3
"""
RCB Tactical Usage Patterns - Deep Dive Query
===============================================
Queries DuckDB for RCB batting order patterns, bowling deployment,
and match-context-based tactical decisions since 2023.
"""

import duckdb
import pandas as pd

pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 200)
pd.set_option("display.max_rows", 100)

DB_PATH = "/Users/dwijeshreddy/cricket-playbook/data/cricket_playbook.duckdb"
con = duckdb.connect(DB_PATH, read_only=True)

RCB_IDS = "('efea6f0477c9', 'bf338eb11095')"  # Bangalore + Bengaluru
RCB_LIKE = "%Royal Challengers%"

separator = "=" * 100

# =====================================================================
# SECTION 1: BATTING ORDER BY MATCH SITUATION
# =====================================================================
print(f"\n{separator}")
print("SECTION 1: RCB BATTING ORDER BY MATCH SITUATION (2023-2025)")
print(separator)

# 1A: Batting order flexibility (from pre-built view)
print("\n--- 1A: BATTING POSITION SHIFTS BY WICKET SITUATION ---")
q = f"""
SELECT batter_name,
       SUM(innings_count) as total_innings,
       ROUND(AVG(avg_batting_position), 2) as overall_avg_pos,
       ROUND(AVG(avg_position_0_wickets), 2) as pos_0_wkts,
       ROUND(AVG(avg_position_1_wicket), 2) as pos_1_wkt,
       ROUND(AVG(avg_position_2plus_wickets), 2) as pos_2plus_wkts
FROM analytics_ipl_batting_order_flexibility_since2023
WHERE team_name LIKE '{RCB_LIKE}'
GROUP BY batter_name
HAVING SUM(innings_count) >= 5
ORDER BY overall_avg_pos
"""
df = con.execute(q).fetchdf()
print(df.to_string(index=False))

# 1B: Detailed entry point analysis for key batters
print("\n--- 1B: ENTRY POINT ANALYSIS (KEY BATTERS) ---")

q = f"""
SELECT batter_name,
       COUNT(*) as innings,
       ROUND(AVG(entry_over), 1) as avg_entry_over,
       ROUND(AVG(batting_position), 1) as avg_bat_pos,
       ROUND(MIN(entry_over), 1) as earliest_entry,
       ROUND(MAX(entry_over), 1) as latest_entry,
       ROUND(AVG(team_wickets_at_entry), 1) as avg_wkts_at_entry,
       ROUND(AVG(team_score_at_entry), 1) as avg_score_at_entry
FROM analytics_ipl_batter_entry_point_since2023
WHERE team_name LIKE '{RCB_LIKE}'
GROUP BY batter_name
HAVING COUNT(*) >= 5
ORDER BY avg_entry_over
"""
df = con.execute(q).fetchdf()
print(df.to_string(index=False))

# 1C: Batting position distribution (how many times at each position)
print("\n--- 1C: BATTING POSITION DISTRIBUTION (TIMES AT EACH POSITION) ---")
q = f"""
WITH pos_data AS (
    SELECT batter_name, batting_position, COUNT(*) as times
    FROM analytics_ipl_batter_entry_point_since2023
    WHERE team_name LIKE '{RCB_LIKE}'
    GROUP BY batter_name, batting_position
),
total AS (
    SELECT batter_name, SUM(times) as total_innings
    FROM pos_data
    GROUP BY batter_name
    HAVING SUM(times) >= 5
)
SELECT p.batter_name,
       t.total_innings,
       SUM(CASE WHEN batting_position = 1 THEN times ELSE 0 END) as pos_1,
       SUM(CASE WHEN batting_position = 2 THEN times ELSE 0 END) as pos_2,
       SUM(CASE WHEN batting_position = 3 THEN times ELSE 0 END) as pos_3,
       SUM(CASE WHEN batting_position = 4 THEN times ELSE 0 END) as pos_4,
       SUM(CASE WHEN batting_position = 5 THEN times ELSE 0 END) as pos_5,
       SUM(CASE WHEN batting_position = 6 THEN times ELSE 0 END) as pos_6,
       SUM(CASE WHEN batting_position = 7 THEN times ELSE 0 END) as pos_7,
       SUM(CASE WHEN batting_position >= 8 THEN times ELSE 0 END) as pos_8plus
FROM pos_data p
JOIN total t ON p.batter_name = t.batter_name
GROUP BY p.batter_name, t.total_innings
ORDER BY
    CASE WHEN SUM(CASE WHEN batting_position = 1 THEN times ELSE 0 END) > 0 THEN 1
         WHEN SUM(CASE WHEN batting_position = 2 THEN times ELSE 0 END) > 0 THEN 2
         WHEN SUM(CASE WHEN batting_position = 3 THEN times ELSE 0 END) > 0 THEN 3
         ELSE 4 END,
    t.total_innings DESC
"""
df = con.execute(q).fetchdf()
print(df.to_string(index=False))

# 1D: Setting vs Chasing batting order
print("\n--- 1D: BATTING ORDER - SETTING vs CHASING ---")
q = f"""
SELECT batter_name,
       CASE WHEN chase_target IS NULL OR chase_target = 0 THEN 'Setting' ELSE 'Chasing' END as context,
       COUNT(*) as innings,
       ROUND(AVG(batting_position), 2) as avg_bat_pos,
       ROUND(AVG(entry_over), 1) as avg_entry_over
FROM analytics_ipl_batter_entry_point_since2023
WHERE team_name LIKE '{RCB_LIKE}'
GROUP BY batter_name, context
HAVING COUNT(*) >= 3
ORDER BY batter_name, context
"""
df = con.execute(q).fetchdf()
pivot = df.pivot_table(
    index="batter_name",
    columns="context",
    values=["avg_bat_pos", "avg_entry_over", "innings"],
    aggfunc="first",
)
pivot.columns = [f"{col[0]}_{col[1]}" for col in pivot.columns]
pivot = pivot.reset_index()
cols_order = ["batter_name"]
for ctx in ["Setting", "Chasing"]:
    for metric in ["innings", "avg_bat_pos", "avg_entry_over"]:
        col = f"{metric}_{ctx}"
        if col in pivot.columns:
            cols_order.append(col)
pivot = pivot[[c for c in cols_order if c in pivot.columns]]
pivot = pivot.sort_values("avg_bat_pos_Setting", na_position="last")
print(pivot.to_string(index=False))

# 1E: Early collapse vs stable start batting order
print("\n--- 1E: BATTING ORDER UNDER EARLY PRESSURE (2+ WICKETS IN PP vs 0-1) ---")
q = f"""
WITH pp_wickets AS (
    SELECT fb.match_id, fb.innings,
           SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as pp_wkts
    FROM fact_ball fb
    JOIN dim_match dm ON fb.match_id = dm.match_id
    WHERE fb.batting_team_id IN {RCB_IDS}
      AND dm.season IN ('2023', '2024', '2025')
      AND fb.over < 6
    GROUP BY fb.match_id, fb.innings
),
entry_with_pp AS (
    SELECT e.*, pw.pp_wkts,
           CASE WHEN pw.pp_wkts >= 2 THEN 'Early Collapse (2+ PP wkts)'
                ELSE 'Stable Start (0-1 PP wkts)' END as pp_situation
    FROM analytics_ipl_batter_entry_point_since2023 e
    JOIN pp_wickets pw ON e.match_id = pw.match_id AND e.innings = pw.innings
    WHERE e.team_name LIKE '{RCB_LIKE}'
)
SELECT batter_name, pp_situation,
       COUNT(*) as innings,
       ROUND(AVG(batting_position), 2) as avg_pos,
       ROUND(AVG(entry_over), 1) as avg_entry_over
FROM entry_with_pp
GROUP BY batter_name, pp_situation
HAVING COUNT(*) >= 2
ORDER BY batter_name, pp_situation
"""
df = con.execute(q).fetchdf()
pivot2 = df.pivot_table(
    index="batter_name",
    columns="pp_situation",
    values=["avg_pos", "avg_entry_over", "innings"],
    aggfunc="first",
)
pivot2.columns = [f"{col[1][:8]}_{col[0]}" for col in pivot2.columns]
pivot2 = pivot2.reset_index()
print(pivot2.to_string(index=False))


# =====================================================================
# SECTION 2: BOWLING DEPLOYMENT ACROSS 20 OVERS
# =====================================================================
print(f"\n\n{separator}")
print("SECTION 2: RCB BOWLING DEPLOYMENT ACROSS 20 OVERS (2023-2025)")
print(separator)

# 2A: Key bowler over-by-over breakdown
print("\n--- 2A: KEY BOWLER OVER-BY-OVER DEPLOYMENT ---")
KEY_BOWLERS = [
    "JR Hazlewood",
    "B Kumar",
    "Suyash Sharma",
    "KH Pandya",
    "Mohammed Siraj",
    "Yash Dayal",
    "HV Patel",
    "Vijaykumar Vyshak",
    "C Green",
    "KV Sharma",
]

BOWLER_TYPES = {
    "JR Hazlewood": "PACE",
    "Mohammed Siraj": "PACE",
    "B Kumar": "PACE",
    "Yash Dayal": "PACE",
    "Vijaykumar Vyshak": "PACE",
    "C Green": "PACE",
    "Suyash Sharma": "SPIN",
    "KV Sharma": "SPIN",
    "HV Patel": "SPIN",
    "KH Pandya": "SPIN",
}

q = f"""
WITH rcb_bowling AS (
    SELECT fb.bowler_id, p.current_name as bowler_name,
           fb.over + 1 as over_number,
           COUNT(CASE WHEN fb.is_legal_ball THEN 1 END) as balls,
           SUM(fb.total_runs) as runs,
           SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as wickets,
           COUNT(DISTINCT fb.match_id || '-' || CAST(fb.innings AS VARCHAR)) as times_bowled
    FROM fact_ball fb
    JOIN dim_match dm ON fb.match_id = dm.match_id
    JOIN dim_player p ON fb.bowler_id = p.player_id
    WHERE fb.bowling_team_id IN {RCB_IDS}
      AND dm.season IN ('2023', '2024', '2025')
    GROUP BY fb.bowler_id, p.current_name, fb.over
)
SELECT bowler_name, over_number, times_bowled, balls,
       runs, wickets,
       ROUND(runs * 6.0 / NULLIF(balls, 0), 2) as economy
FROM rcb_bowling
WHERE bowler_name IN ('JR Hazlewood', 'B Kumar', 'Suyash Sharma',
                      'Mohammed Siraj', 'Yash Dayal', 'HV Patel',
                      'Vijaykumar Vyshak', 'KH Pandya', 'C Green', 'KV Sharma')
ORDER BY bowler_name, over_number
"""
df = con.execute(q).fetchdf()

for bowler in KEY_BOWLERS:
    bdf = df[df["bowler_name"] == bowler]
    if bdf.empty:
        continue
    print(f"\n  {bowler} ({BOWLER_TYPES.get(bowler, '?')})")
    print(f"  {'Over':<6} {'Times':>6} {'Balls':>6} {'Runs':>6} {'Wkts':>6} {'Econ':>7}")
    print(f"  {'-' * 37}")
    total_balls, total_runs, total_wkts = 0, 0, 0
    for _, r in bdf.iterrows():
        ov = int(r["over_number"])
        phase = "PP" if ov <= 6 else ("MID" if ov <= 15 else "DTH")
        print(
            f"  {ov:<3}({phase}) {int(r['times_bowled']):>4}   {int(r['balls']):>5}  {int(r['runs']):>5}  {int(r['wickets']):>5}  {r['economy']:>6}"
        )
        total_balls += int(r["balls"])
        total_runs += int(r["runs"])
        total_wkts += int(r["wickets"])
    overall_econ = round(total_runs * 6.0 / total_balls, 2) if total_balls > 0 else 0
    print(
        f"  {'TOTAL':<10} {'-':>3}   {total_balls:>5}  {total_runs:>5}  {total_wkts:>5}  {overall_econ:>6}"
    )

# 2B: Hazlewood specific - PP vs Death usage
print("\n--- 2B: HAZLEWOOD PP vs DEATH USAGE ---")
q = f"""
WITH hz AS (
    SELECT fb.match_id, fb.innings, fb.over + 1 as over_num,
           CASE WHEN fb.over < 6 THEN 'PP (1-6)'
                WHEN fb.over >= 15 THEN 'Death (16-20)'
                ELSE 'Middle (7-15)' END as phase,
           COUNT(CASE WHEN fb.is_legal_ball THEN 1 END) as balls,
           SUM(fb.total_runs) as runs,
           SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as wkts
    FROM fact_ball fb
    JOIN dim_match dm ON fb.match_id = dm.match_id
    WHERE fb.bowling_team_id IN {RCB_IDS}
      AND dm.season IN ('2023', '2024', '2025')
      AND fb.bowler_id = '03806cf8'
    GROUP BY fb.match_id, fb.innings, fb.over
)
SELECT phase,
       COUNT(*) as overs_bowled,
       SUM(balls) as total_balls,
       SUM(runs) as total_runs,
       SUM(wkts) as total_wkts,
       ROUND(SUM(runs) * 6.0 / NULLIF(SUM(balls), 0), 2) as economy,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM hz), 1) as pct_of_overs
FROM hz
GROUP BY phase
ORDER BY CASE phase WHEN 'PP (1-6)' THEN 1 WHEN 'Middle (7-15)' THEN 2 ELSE 3 END
"""
df = con.execute(q).fetchdf()
print(df.to_string(index=False))

# 2C: Team-level pace vs spin by over
print("\n--- 2C: TEAM-LEVEL PACE vs SPIN BY OVER ---")
q = f"""
WITH bowl_type_map AS (
    SELECT fb.bowler_id, p.current_name,
           fb.over + 1 as over_num,
           fb.match_id, fb.innings,
           COUNT(CASE WHEN fb.is_legal_ball THEN 1 END) as balls,
           SUM(fb.total_runs) as runs,
           SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as wkts
    FROM fact_ball fb
    JOIN dim_match dm ON fb.match_id = dm.match_id
    JOIN dim_player p ON fb.bowler_id = p.player_id
    WHERE fb.bowling_team_id IN {RCB_IDS}
      AND dm.season IN ('2023', '2024', '2025')
    GROUP BY fb.bowler_id, p.current_name, fb.over, fb.match_id, fb.innings
)
SELECT over_num,
       SUM(balls) as total_balls,
       SUM(runs) as total_runs,
       ROUND(SUM(runs) * 6.0 / NULLIF(SUM(balls), 0), 2) as economy,
       SUM(CASE WHEN current_name IN ('JR Hazlewood','Mohammed Siraj','B Kumar','Yash Dayal',
           'Vijaykumar Vyshak','C Green','Akash Deep','WD Parnell','LH Ferguson',
           'RJW Topley','DJ Willey','AS Joseph','L Ngidi','Rasikh Salam','R Shepherd')
           THEN balls ELSE 0 END) as pace_balls,
       SUM(CASE WHEN current_name IN ('Suyash Sharma','KV Sharma','HV Patel','GJ Maxwell',
           'KH Pandya','PWH de Silva','Swapnil Singh','MK Lomror','Shahbaz Ahmed',
           'Mayank Dagar','MG Bracewell','WG Jacks','LS Livingstone')
           THEN balls ELSE 0 END) as spin_balls
FROM bowl_type_map
GROUP BY over_num
ORDER BY over_num
"""
df = con.execute(q).fetchdf()
df["pace_pct"] = (df["pace_balls"] * 100.0 / df["total_balls"]).round(1)
df["spin_pct"] = (df["spin_balls"] * 100.0 / df["total_balls"]).round(1)

print(f"  {'Over':<6} {'Balls':>6} {'Runs':>6} {'Econ':>6} {'Pace%':>7} {'Spin%':>7}")
print(f"  {'-' * 44}")
for _, r in df.iterrows():
    ov = int(r["over_num"])
    phase = "PP" if ov <= 6 else ("MID" if ov <= 15 else "DTH")
    print(
        f"  {ov:<3}({phase}) {int(r['total_balls']):>5}  {int(r['total_runs']):>5}  {r['economy']:>5}  {r['pace_pct']:>6}  {r['spin_pct']:>6}"
    )

mid_spin = df[(df["over_num"] >= 7) & (df["over_num"] <= 15)]
total_mid_balls = mid_spin["total_balls"].sum()
total_spin_balls = mid_spin["spin_balls"].sum()
spin_pct_mid = round(total_spin_balls * 100.0 / total_mid_balls, 1) if total_mid_balls > 0 else 0
total_mid_matches_approx = total_mid_balls / (9 * 6)  # ~9 overs * 6 balls
spin_overs_per_match_mid = (
    round(total_spin_balls / 6.0 / total_mid_matches_approx, 1)
    if total_mid_matches_approx > 0
    else 0
)

print(f"\n  SPIN IN MIDDLE OVERS (7-15): {spin_pct_mid}% of deliveries")
print(f"  Approx {spin_overs_per_match_mid} spin overs per match in middle phase (out of 9)")

# 2D: Bowler phase distribution from pre-built view
print("\n--- 2D: KEY BOWLER PHASE DISTRIBUTION (from analytics view) ---")
q = """
SELECT bowler_name, match_phase, overs, runs_conceded, wickets,
       economy, dot_ball_pct, pct_overs_in_phase, sample_size
FROM analytics_ipl_bowler_phase_distribution_since2023
WHERE bowler_name IN ('JR Hazlewood', 'B Kumar', 'Suyash Sharma',
                      'Mohammed Siraj', 'Yash Dayal', 'HV Patel',
                      'Vijaykumar Vyshak', 'KH Pandya')
ORDER BY bowler_name,
    CASE match_phase WHEN 'powerplay' THEN 1 WHEN 'middle' THEN 2 WHEN 'death' THEN 3 END
"""
df = con.execute(q).fetchdf()
print(df.to_string(index=False))


# =====================================================================
# SECTION 3: MATCH CONTEXT DEPLOYMENT
# =====================================================================
print(f"\n\n{separator}")
print("SECTION 3: MATCH CONTEXT DEPLOYMENT (2023-2025)")
print(separator)

# 3A: Bowling deployment when bowling first vs second
print("\n--- 3A: BOWLING DEPLOYMENT BY INNINGS (BOWL 1ST vs 2ND) ---")
q = f"""
WITH bowl_context AS (
    SELECT p.current_name as bowler_name,
           fb.innings,
           CASE WHEN fb.innings = 1 THEN 'Bowl 1st (Setting Target)'
                ELSE 'Bowl 2nd (Defending)' END as context,
           CASE WHEN fb.over < 6 THEN 'PP'
                WHEN fb.over < 15 THEN 'Middle'
                ELSE 'Death' END as phase,
           COUNT(CASE WHEN fb.is_legal_ball THEN 1 END) as balls,
           SUM(fb.total_runs) as runs,
           SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as wkts
    FROM fact_ball fb
    JOIN dim_match dm ON fb.match_id = dm.match_id
    JOIN dim_player p ON fb.bowler_id = p.player_id
    WHERE fb.bowling_team_id IN {RCB_IDS}
      AND dm.season IN ('2023', '2024', '2025')
      AND p.current_name IN ('JR Hazlewood', 'B Kumar', 'Suyash Sharma',
                             'Mohammed Siraj', 'Yash Dayal', 'HV Patel',
                             'Vijaykumar Vyshak', 'KH Pandya')
    GROUP BY p.current_name, fb.innings, fb.over
)
SELECT bowler_name, context, phase,
       SUM(balls) as balls,
       SUM(runs) as runs,
       SUM(wkts) as wkts,
       ROUND(SUM(runs) * 6.0 / NULLIF(SUM(balls), 0), 2) as economy
FROM bowl_context
GROUP BY bowler_name, context, phase
ORDER BY bowler_name, context,
    CASE phase WHEN 'PP' THEN 1 WHEN 'Middle' THEN 2 ELSE 3 END
"""
df = con.execute(q).fetchdf()
print(df.to_string(index=False))

# 3B: Team-level pace vs spin by phase, split by innings context
print("\n--- 3B: TEAM-LEVEL PACE vs SPIN BY PHASE & INNINGS CONTEXT ---")
q = f"""
WITH bowl_typed AS (
    SELECT fb.innings,
           CASE WHEN fb.innings = 1 THEN 'Bowl 1st' ELSE 'Bowl 2nd' END as context,
           CASE WHEN fb.over < 6 THEN 'PP (1-6)'
                WHEN fb.over < 15 THEN 'Middle (7-15)'
                ELSE 'Death (16-20)' END as phase,
           CASE WHEN p.current_name IN ('JR Hazlewood','Mohammed Siraj','B Kumar','Yash Dayal',
               'Vijaykumar Vyshak','C Green','Akash Deep','WD Parnell','LH Ferguson',
               'RJW Topley','DJ Willey','AS Joseph','L Ngidi','Rasikh Salam','R Shepherd')
               THEN 'Pace'
               WHEN p.current_name IN ('Suyash Sharma','KV Sharma','HV Patel','GJ Maxwell',
               'KH Pandya','PWH de Silva','Swapnil Singh','MK Lomror','Shahbaz Ahmed',
               'Mayank Dagar','MG Bracewell','WG Jacks','LS Livingstone')
               THEN 'Spin'
               ELSE 'Unknown' END as bowl_type,
           COUNT(CASE WHEN fb.is_legal_ball THEN 1 END) as balls,
           SUM(fb.total_runs) as runs,
           SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as wkts
    FROM fact_ball fb
    JOIN dim_match dm ON fb.match_id = dm.match_id
    JOIN dim_player p ON fb.bowler_id = p.player_id
    WHERE fb.bowling_team_id IN {RCB_IDS}
      AND dm.season IN ('2023', '2024', '2025')
    GROUP BY fb.innings, p.current_name, fb.over
)
SELECT context, phase, bowl_type,
       SUM(balls) as balls,
       ROUND(SUM(balls) / 6.0, 1) as overs,
       SUM(runs) as runs,
       SUM(wkts) as wkts,
       ROUND(SUM(runs) * 6.0 / NULLIF(SUM(balls), 0), 2) as economy,
       ROUND(SUM(balls) * 100.0 / SUM(SUM(balls)) OVER (PARTITION BY context, phase), 1) as pct_of_phase
FROM bowl_typed
WHERE bowl_type != 'Unknown'
GROUP BY context, phase, bowl_type
ORDER BY context,
    CASE phase WHEN 'PP (1-6)' THEN 1 WHEN 'Middle (7-15)' THEN 2 ELSE 3 END,
    bowl_type
"""
df = con.execute(q).fetchdf()
print(df.to_string(index=False))

# 3C: Season-by-season changes
print("\n--- 3C: SEASON-BY-SEASON SPIN ALLOCATION IN MIDDLE OVERS ---")
q = f"""
WITH bowl_typed AS (
    SELECT dm.season,
           fb.over + 1 as over_num,
           CASE WHEN p.current_name IN ('Suyash Sharma','KV Sharma','HV Patel','GJ Maxwell',
               'KH Pandya','PWH de Silva','Swapnil Singh','MK Lomror','Shahbaz Ahmed',
               'Mayank Dagar','MG Bracewell','WG Jacks','LS Livingstone')
               THEN 'Spin' ELSE 'Pace' END as bowl_type,
           COUNT(CASE WHEN fb.is_legal_ball THEN 1 END) as balls
    FROM fact_ball fb
    JOIN dim_match dm ON fb.match_id = dm.match_id
    JOIN dim_player p ON fb.bowler_id = p.player_id
    WHERE fb.bowling_team_id IN {RCB_IDS}
      AND dm.season IN ('2023', '2024', '2025')
      AND fb.over >= 6 AND fb.over < 15
    GROUP BY dm.season, fb.over, p.current_name
)
SELECT season,
       SUM(CASE WHEN bowl_type = 'Spin' THEN balls ELSE 0 END) as spin_balls,
       SUM(CASE WHEN bowl_type = 'Pace' THEN balls ELSE 0 END) as pace_balls,
       SUM(balls) as total_balls,
       ROUND(SUM(CASE WHEN bowl_type = 'Spin' THEN balls ELSE 0 END) * 100.0 / SUM(balls), 1) as spin_pct
FROM bowl_typed
GROUP BY season
ORDER BY season
"""
df = con.execute(q).fetchdf()
print(df.to_string(index=False))


# =====================================================================
# SECTION 4: KEY INSIGHTS SUMMARY
# =====================================================================
print(f"\n\n{separator}")
print("SECTION 4: KEY TACTICAL INSIGHTS")
print(separator)

# Hazlewood death overs
q = f"""
WITH hz_matches AS (
    SELECT DISTINCT fb.match_id
    FROM fact_ball fb
    JOIN dim_match dm ON fb.match_id = dm.match_id
    WHERE fb.bowler_id = '03806cf8'
      AND fb.bowling_team_id IN {RCB_IDS}
      AND dm.season IN ('2023', '2024', '2025')
),
hz_death AS (
    SELECT fb.match_id,
           SUM(CASE WHEN fb.over >= 15 AND fb.is_legal_ball THEN 1 ELSE 0 END) as death_balls
    FROM fact_ball fb
    WHERE fb.bowler_id = '03806cf8'
      AND fb.match_id IN (SELECT match_id FROM hz_matches)
    GROUP BY fb.match_id
)
SELECT COUNT(*) as total_matches,
       SUM(CASE WHEN death_balls > 0 THEN 1 ELSE 0 END) as matches_bowled_at_death,
       ROUND(SUM(CASE WHEN death_balls > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pct_death_usage,
       ROUND(AVG(CASE WHEN death_balls > 0 THEN death_balls / 6.0 END), 1) as avg_death_overs_when_used
FROM hz_death
"""
hz_death = con.execute(q).fetchdf()

print(f"""
1. HAZLEWOOD DEATH DEPLOYMENT:
   - Bowled at death in {hz_death["matches_bowled_at_death"].values[0]} of {hz_death["total_matches"].values[0]} matches ({hz_death["pct_death_usage"].values[0]}%)
   - NOT a PP-only bowler; RCB saves overs for death regularly
""")

# Patidar flexibility
q = f"""
SELECT
    ROUND(AVG(CASE WHEN team_wickets_at_entry <= 1 THEN batting_position END), 2) as pos_stable,
    ROUND(AVG(CASE WHEN team_wickets_at_entry >= 2 THEN batting_position END), 2) as pos_collapse,
    ROUND(AVG(CASE WHEN team_wickets_at_entry <= 1 THEN entry_over END), 1) as entry_stable,
    ROUND(AVG(CASE WHEN team_wickets_at_entry >= 2 THEN entry_over END), 1) as entry_collapse
FROM analytics_ipl_batter_entry_point_since2023
WHERE batter_name = 'RM Patidar'
  AND team_name LIKE '{RCB_LIKE}'
"""
pat = con.execute(q).fetchdf()
print(f"""2. PATIDAR AS BATTING ANCHOR:
   - Stable start (0-1 wkts): Avg position {pat["pos_stable"].values[0]}, entry over {pat["entry_stable"].values[0]}
   - Under pressure (2+ wkts): Avg position {pat["pos_collapse"].values[0]}, entry over {pat["entry_collapse"].values[0]}
   - Floats up when wickets fall early - key stabilizer
""")

# Tim David and Krunal entry points
q = f"""
SELECT batter_name,
       COUNT(*) as innings,
       ROUND(AVG(entry_over), 1) as avg_entry,
       ROUND(AVG(batting_position), 1) as avg_pos,
       ROUND(AVG(team_score_at_entry), 0) as avg_team_score
FROM analytics_ipl_batter_entry_point_since2023
WHERE batter_name IN ('TH David', 'KH Pandya')
  AND team_name LIKE '{RCB_LIKE}'
GROUP BY batter_name
"""
fin = con.execute(q).fetchdf()
print("3. FINISHER DEPLOYMENT:")
for _, r in fin.iterrows():
    print(
        f"   - {r['batter_name']}: Enters at over {r['avg_entry']}, position {r['avg_pos']}, team score ~{int(r['avg_team_score'])}"
    )

print(f"""
4. SPIN IN MIDDLE OVERS:
   - RCB uses spin for {spin_pct_mid}% of middle-over deliveries
   - ~{spin_overs_per_match_mid} spin overs per match in overs 7-15
   - Philosophy: spin to strangle in middle, pace to dominate PP and death
""")

# Bhuvi death specialist check
q = f"""
WITH bk AS (
    SELECT CASE WHEN fb.over < 6 THEN 'PP'
                WHEN fb.over < 15 THEN 'Middle'
                ELSE 'Death' END as phase,
           COUNT(CASE WHEN fb.is_legal_ball THEN 1 END) as balls,
           SUM(fb.total_runs) as runs,
           SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as wkts
    FROM fact_ball fb
    JOIN dim_match dm ON fb.match_id = dm.match_id
    WHERE fb.bowler_id = '2e81a32d'
      AND fb.bowling_team_id IN {RCB_IDS}
      AND dm.season IN ('2023', '2024', '2025')
    GROUP BY phase
)
SELECT phase, balls, runs, wkts,
       ROUND(runs * 6.0 / NULLIF(balls, 0), 2) as economy
FROM bk
ORDER BY CASE phase WHEN 'PP' THEN 1 WHEN 'Middle' THEN 2 ELSE 3 END
"""
bk_df = con.execute(q).fetchdf()
print("5. BHUVNESHWAR KUMAR PHASE SPLIT:")
for _, r in bk_df.iterrows():
    print(f"   - {r['phase']}: {int(r['balls'])} balls, econ {r['economy']}, {int(r['wkts'])} wkts")

# Jitesh Sharma entry
q = f"""
SELECT batter_name,
       COUNT(*) as innings,
       ROUND(AVG(entry_over), 1) as avg_entry,
       ROUND(AVG(batting_position), 1) as avg_pos,
       ROUND(MIN(entry_over), 1) as earliest,
       ROUND(MAX(entry_over), 1) as latest
FROM analytics_ipl_batter_entry_point_since2023
WHERE batter_name = 'JM Sharma'
  AND team_name LIKE '{RCB_LIKE}'
GROUP BY batter_name
"""
jit = con.execute(q).fetchdf()
if not jit.empty:
    r = jit.iloc[0]
    print(f"""
6. JITESH SHARMA DEPLOYMENT:
   - {int(r["innings"])} innings, avg entry over {r["avg_entry"]}, avg position {r["avg_pos"]}
   - Range: entered as early as over {r["earliest"]} and as late as over {r["latest"]}
   - Pure designated finisher role
""")

# Venkatesh Iyer check
q = """
SELECT batter_name, team_name, COUNT(*) as innings,
       ROUND(AVG(entry_over), 1) as avg_entry,
       ROUND(AVG(batting_position), 1) as avg_pos
FROM analytics_ipl_batter_entry_point_since2023
WHERE batter_name LIKE '%V Iyer%' OR batter_name LIKE '%Venkatesh%'
GROUP BY batter_name, team_name
"""
vi = con.execute(q).fetchdf()
if not vi.empty:
    print("7. VENKATESH IYER DATA:")
    print(f"   {vi.to_string(index=False)}")
    print("   Note: Check if V Iyer was acquired by RCB for 2026 mega auction")
else:
    print("7. VENKATESH IYER: No data found in since2023 views. May be a 2026 auction acquisition.")

con.close()

print(f"\n{separator}")
print("END OF RCB TACTICAL USAGE REPORT")
print(separator)
