# EPIC PRD: Player Profile View

**Epic Name:** Player Profile View
**Epic Owner:** Tom Brady (Product Owner)
**Priority:** P1 - High
**Status:** APPROVED - Florentino Gate Passed 2026-02-13
**Created:** 2026-02-06
**Version:** 1.0.0

---

## 1. Overview

### 1.1 Epic Summary

| Field | Value |
|-------|-------|
| Epic Name | Player Profile View |
| Owner | Tom Brady (Product Owner) |
| Priority | P1 - High (Founder Requested) |
| Target Release | IPL 2026 Pre-Tournament Magazine |
| Dependencies | Tags, Matchups, Clustering (All Complete) |

### 1.2 Problem Statement

Currently, The Lab's Teams section displays player names without any interactivity. Readers who want to understand a player's profile must:

1. Leave the application and search external sources
2. Cross-reference multiple data points manually
3. Lack context on player role, strengths, and vulnerabilities

This creates friction that disrupts the reading experience and fails to surface our existing player data. **We have all the data - it's just not surfaced to users.**

### 1.3 User Story

> As a cricket analyst viewing a team's roster in The Lab,
> I want to click on any player's name and see a comprehensive profile modal,
> So that I can quickly understand the player's IPL performance, role, matchup tendencies, and strategic value without leaving the current view.

### 1.4 Founder Mandate

The Founder specifically requested:

> "When anyone clicks on a player's name in the Teams section, we should show:
> - Player's IPL numbers since 2023
> - Role tags (SPECIALIST, VULNERABLE, CONSISTENT, etc.)
> - Matchup numbers (vs specific teams, bowling types, etc.)
> - Entry points for batters
> - Bowler types and classifications
> - Archetypes (cluster labels)
> - Matchup tags
> - All relevant information in a concise manner"

**Key Constraint:** Concise. This is a quick-reference modal, not a full scouting report.

---

## 2. Scope

### 2.1 V1 Scope (In Scope)

| Feature | Description | Data Source |
|---------|-------------|-------------|
| Player Header | Name, team, role, contract price | `ipl_2026_squads`, `ipl_2026_contracts` |
| Career Stats (IPL 2023+) | Runs/Wickets, Avg, SR/Econ | `analytics_ipl_batting_career`, `analytics_ipl_bowling_career` |
| Phase Performance | PP, Middle, Death breakdown | `analytics_ipl_batter_phase`, `analytics_ipl_bowler_phase` |
| Role Tags | SPECIALIST_VS_*, VULNERABLE_VS_*, PP_DOMINATOR, etc. | `player_tags_2023.json` |
| Cluster/Archetype | K-means cluster label (e.g., "Power Finisher") | `player_clustering_2023.csv` |
| vs Team Matchups | Performance vs each IPL team | `analytics_ipl_batter_vs_team`, `analytics_ipl_bowler_vs_team` |
| vs Bowling Type (Batters) | SR vs pace, spin, leg-spin, off-spin, etc. | `batter_bowling_type_detail_2023.csv` |
| vs Batting Hand (Bowlers) | Economy/SR vs LHB, RHB | `bowler_handedness_matchup_2023.csv` |
| Entry Point (Batters) | Avg entry ball, classification | `batter_entry_points_2023.csv` |
| Bowler Classification | Type (Fast, Off-spin, etc.), arm | `ipl_2026_squads` |

### 2.2 V2 Scope (Deferred)

| Feature | Reason for Deferral |
|---------|---------------------|
| Historical trend charts | Requires charting library integration |
| Head-to-head vs specific bowlers/batters | Data exists but UI complexity high |
| Venue-specific performance | Secondary importance, adds clutter |
| Comparison mode (side-by-side players) | Feature creep; evaluate after V1 |
| Video highlights integration | External dependency, licensing concerns |
| Form indicator (last 5 matches) | Requires real-time data pipeline |
| Injury status | External data source required |
| Fantasy points integration | Out of scope for magazine product |

---

## 3. Data Requirements

### 3.1 All Data Fields to Display

#### Header Section
| Field | Source | Notes |
|-------|--------|-------|
| `player_name` | `dim_player.current_name` | Display name |
| `player_id` | `dim_player.player_id` | Internal reference |
| `team_name` | `ipl_2026_squads.team_name` | Current IPL franchise |
| `role` | `ipl_2026_squads.role` | Batter/Bowler/All-rounder/Wicketkeeper |
| `price_cr` | `ipl_2026_contracts.price_cr` | Contract value |
| `acquisition_type` | `ipl_2026_contracts.acquisition_type` | Retained/RTM/Auction |
| `archetype` | `player_clustering_2023.csv` | K-means cluster label |

#### Batter-Specific Fields
| Field | Source | Notes |
|-------|--------|-------|
| `runs` | `analytics_ipl_batting_career` | Total runs (2023+) |
| `innings` | `analytics_ipl_batting_career` | Innings batted |
| `balls_faced` | `analytics_ipl_batting_career` | Total balls |
| `average` | `analytics_ipl_batting_career` | Batting average |
| `strike_rate` | `analytics_ipl_batting_career` | Overall SR |
| `fifties` | `analytics_ipl_batting_career` | 50s scored |
| `hundreds` | `analytics_ipl_batting_career` | 100s scored |
| `fours` | `analytics_ipl_batting_career` | 4s hit |
| `sixes` | `analytics_ipl_batting_career` | 6s hit |
| `boundary_pct` | `analytics_ipl_batting_career` | Boundary percentage |
| `dot_ball_pct` | `analytics_ipl_batting_career` | Dot ball percentage |
| `pp_sr`, `pp_avg`, `pp_boundary_pct` | `analytics_ipl_batter_phase` | Powerplay metrics |
| `mid_sr`, `mid_avg`, `mid_boundary_pct` | `analytics_ipl_batter_phase` | Middle overs metrics |
| `death_sr`, `death_avg`, `death_boundary_pct` | `analytics_ipl_batter_phase` | Death overs metrics |
| `entry_point_classification` | `batter_entry_points_2023.csv` | TOP_ORDER/MIDDLE_ORDER/FINISHER |
| `avg_entry_ball` | `batter_entry_points_2023.csv` | Average entry ball number |
| `vs_pace_sr`, `vs_pace_avg` | `batter_bowling_type_matchup_2023.csv` | vs Pace performance |
| `vs_spin_sr`, `vs_spin_avg` | `batter_bowling_type_matchup_2023.csv` | vs Spin performance |
| `vs_leg_spin_sr` | `batter_bowling_type_detail_2023.csv` | vs Leg-spin specifically |
| `vs_off_spin_sr` | `batter_bowling_type_detail_2023.csv` | vs Off-spin specifically |
| `vs_left_arm_spin_sr` | `batter_bowling_type_detail_2023.csv` | vs Left-arm orthodox |
| `tags` | `player_tags_2023.json` | Array of role tags |

#### Bowler-Specific Fields
| Field | Source | Notes |
|-------|--------|-------|
| `wickets` | `analytics_ipl_bowling_career` | Total wickets (2023+) |
| `overs` | `analytics_ipl_bowling_career` | Overs bowled |
| `runs_conceded` | `analytics_ipl_bowling_career` | Runs given |
| `economy` | `analytics_ipl_bowling_career` | Economy rate |
| `average` | `analytics_ipl_bowling_career` | Bowling average |
| `strike_rate` | `analytics_ipl_bowling_career` | Bowling SR |
| `dot_ball_pct` | `analytics_ipl_bowling_career` | Dot ball percentage |
| `boundary_pct` | `analytics_ipl_bowling_career` | Boundaries conceded % |
| `pp_economy`, `pp_wickets`, `pp_sr` | `analytics_ipl_bowler_phase` | Powerplay metrics |
| `mid_economy`, `mid_wickets`, `mid_sr` | `analytics_ipl_bowler_phase` | Middle overs metrics |
| `death_economy`, `death_wickets`, `death_sr` | `analytics_ipl_bowler_phase` | Death overs metrics |
| `bowling_arm` | `ipl_2026_squads.bowling_arm` | Right-arm/Left-arm |
| `bowling_type` | `ipl_2026_squads.bowling_type` | Fast/Off-spin/Leg-spin/etc. |
| `lhb_economy`, `lhb_sr` | `bowler_handedness_matchup_2023.csv` | vs Left-hand batters |
| `rhb_economy`, `rhb_sr` | `bowler_handedness_matchup_2023.csv` | vs Right-hand batters |
| `handedness_tags` | `bowler_handedness_matchup_2023.csv` | LHB_SPECIALIST, RHB_SPECIALIST, etc. |
| `tags` | `player_tags_2023.json` | Array of role tags |

### 3.2 Source Tables/Views

| Data Category | Primary Source | Backup/All-Time Source |
|---------------|----------------|------------------------|
| Career Stats | `analytics_ipl_*_career` (2023+ filtered) | Full career views |
| Phase Performance | `analytics_ipl_*_phase` (2023+ filtered) | Full career views |
| Tags & Labels | `outputs/tags/player_tags_2023.json` | `outputs/tags/player_tags.json` |
| Clustering | `outputs/tags/player_clustering_2023.csv` | All-time clustering |
| Entry Points | `outputs/matchups/batter_entry_points_2023.csv` | All-time version |
| Bowling Type Matchups | `outputs/matchups/batter_bowling_type_*_2023.csv` | All-time versions |
| Handedness Matchups | `outputs/matchups/bowler_handedness_matchup_2023.csv` | All-time version |
| Squad/Contract | `ipl_2026_squads`, `ipl_2026_contracts` | N/A |

### 3.3 New Views/Aggregations Needed

| New Requirement | Description | Complexity |
|-----------------|-------------|------------|
| `v_player_profile_batter` | Pre-joined view for batter profiles | Medium |
| `v_player_profile_bowler` | Pre-joined view for bowler profiles | Medium |
| `player_profiles.json` | Pre-computed JSON for all players | Medium |

**Recommendation:** Pre-compute player profiles into a single JSON file per team or a master `player_profiles.json` to avoid multiple data joins at runtime.

---

## 4. User Interface

### 4.1 Modal Design

The player profile appears as a **modal overlay** when clicking a player name. This maintains context (user can see the team behind the modal) while providing detailed information.

```
+---------------------------------------------------------------+
|  [X]                                                           |
|                                                                |
|  VIRAT KOHLI                        Royal Challengers Bengaluru|
|  Batter | Rs. 21.0 Cr (Retained)                               |
|  Archetype: ELITE TOP-ORDER                                    |
|                                                                |
|  +----------------------------------------------------------+  |
|  | CAREER STATS (IPL 2023+)                                 |  |
|  | Runs: 1,483 | Avg: 48.8 | SR: 146.6 | 50s: 12 | 100s: 1  |  |
|  | Balls: 1,011 | Boundary%: 18.4% | Dot%: 32.1%            |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  +----------------------------------------------------------+  |
|  | PHASE PERFORMANCE                                        |  |
|  | PP:     SR 143.2 | Avg 52.3 | Boundary 21.2%             |  |
|  | Middle: SR 148.7 | Avg 46.1 | Boundary 17.8%             |  |
|  | Death:  SR 156.3 | Avg 41.2 | Boundary 19.4%             |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  +----------------------------------------------------------+  |
|  | ROLE TAGS                                                |  |
|  | [SPECIALIST_VS_PACE] [VULNERABLE_VS_SPIN]                |  |
|  | [VULNERABLE_VS_OFF_SPIN] [AGGRESSIVE]                    |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  +----------------------------------------------------------+  |
|  | vs BOWLING TYPE                                          |  |
|  | Pace:     SR 152.3 | Avg 54.2 | 580 balls               |  |
|  | Spin:     SR 138.4 | Avg 41.1 | 431 balls               |  |
|  | Off-spin: SR 129.7 | Avg 32.8 | 198 balls               |  |
|  | Leg-spin: SR 142.1 | Avg 48.3 | 167 balls               |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  +----------------------------------------------------------+  |
|  | vs TEAMS (Top 3 + Bottom 3)                              |  |
|  | Best:  MI (SR 168.4) | SRH (SR 162.1) | PBKS (SR 158.7)  |  |
|  | Worst: DC (SR 118.2) | GT (SR 124.5) | KKR (SR 129.8)    |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  Entry Point: TOP_ORDER (Avg: 2.6 balls)                       |
|                                                                |
+---------------------------------------------------------------+
```

### 4.2 Section Layout

#### For BATTERS:
1. **Header** - Name, Team, Role, Price, Archetype
2. **Career Stats** - Runs, Avg, SR, 50s, 100s, Boundary%, Dot%
3. **Phase Performance** - PP/Middle/Death breakdown
4. **Role Tags** - Visual chips/badges
5. **vs Bowling Type** - Pace vs Spin performance
6. **vs Teams** - Top 3 best + Bottom 3 worst matchups
7. **Entry Point** - Classification + average entry ball

#### For BOWLERS:
1. **Header** - Name, Team, Role, Price, Archetype, Bowling Type
2. **Career Stats** - Wickets, Economy, Avg, SR, Dot%, Boundary%
3. **Phase Performance** - PP/Middle/Death breakdown
4. **Role Tags** - Visual chips/badges
5. **vs Batting Hand** - LHB vs RHB performance
6. **vs Teams** - Top 3 best + Bottom 3 worst matchups
7. **Bowler Classification** - Arm + Type

#### For ALL-ROUNDERS:
Show BOTH batting and bowling sections with a toggle or tabbed interface.

### 4.3 Mobile Considerations

| Aspect | Desktop | Mobile |
|--------|---------|--------|
| Modal Width | 600px centered | Full-screen overlay |
| Sections | Side-by-side where logical | Stacked vertically |
| Font Size | 14px body | 16px body (touch-friendly) |
| Close Button | Top-right X | Top-right X + swipe down |
| Scrolling | Internal scroll | Full-screen scroll |
| Touch Targets | N/A | Minimum 44px height |

### 4.4 Visual Design Principles

1. **Information Density:** High but not overwhelming. Use whitespace strategically.
2. **Scannable:** User should get key insights in <5 seconds.
3. **Consistent:** Same layout for all players, same metrics in same positions.
4. **Actionable Tags:** Color-coded (green = strength, red = vulnerability, blue = neutral).
5. **Sample Size Indicators:** Show "(LOW)" or "(X balls)" for context on metrics.

---

## 5. Player Data Sections - Detailed Specifications

### 5.1 BATTER Profile Sections

#### Section A: Career Stats (IPL 2023+)

**Display Format:**
```
CAREER STATS (IPL 2023+)
Runs: 1,483 | Avg: 48.8 | SR: 146.6
50s: 12 | 100s: 1 | Boundary%: 18.4% | Dot%: 32.1%
```

**Metrics:**
| Metric | Formula | Source |
|--------|---------|--------|
| Runs | SUM(batter_runs) | fact_ball |
| Innings | COUNT(DISTINCT match_id) | fact_ball |
| Average | runs / dismissals | Derived |
| Strike Rate | (runs / balls) * 100 | Derived |
| 50s | COUNT(innings >= 50 AND < 100) | Aggregated |
| 100s | COUNT(innings >= 100) | Aggregated |
| Boundary % | (4s + 6s) / balls * 100 | fact_ball |
| Dot Ball % | dots / balls * 100 | fact_ball |

#### Section B: Phase Performance

**Display Format:**
```
PHASE PERFORMANCE
         SR      Avg     Boundary%  Balls
PP:      143.2   52.3    21.2%      342
Middle:  148.7   46.1    17.8%      456
Death:   156.3   41.2    19.4%      213
```

**Metrics per Phase:**
| Metric | PP (Overs 1-6) | Middle (7-15) | Death (16-20) |
|--------|----------------|---------------|---------------|
| Strike Rate | pp_sr | mid_sr | death_sr |
| Average | pp_avg | mid_avg | death_avg |
| Boundary % | pp_boundary_pct | mid_boundary_pct | death_boundary_pct |
| Balls | pp_balls | mid_balls | death_balls |

#### Section C: Role Tags

**Display Format:**
```
ROLE TAGS
[SPECIALIST_VS_PACE] [VULNERABLE_VS_SPIN]
[VULNERABLE_VS_OFF_SPIN] [AGGRESSIVE]
```

**Tag Categories:**
| Tag Type | Color | Examples |
|----------|-------|----------|
| SPECIALIST_* | Green (#22C55E) | SPECIALIST_VS_PACE, SPECIALIST_VS_SPIN |
| VULNERABLE_* | Red (#EF4444) | VULNERABLE_VS_SPIN, VULNERABLE_VS_LEG_SPIN |
| Phase Strength | Blue (#3B82F6) | PP_DOMINATOR, DEATH_FINISHER |
| Style | Gray (#6B7280) | AGGRESSIVE, PLAYMAKER, SIX_HITTER |

#### Section D: vs Bowling Type Matchups

**Display Format:**
```
vs BOWLING TYPE
              SR      Avg     Balls
Pace:         152.3   54.2    580
Spin:         138.4   41.1    431
 - Off-spin:  129.7   32.8    198
 - Leg-spin:  142.1   48.3    167
 - Left-arm:  145.6   43.2    66
```

**Metrics:**
- Strike Rate vs each type
- Average vs each type
- Sample size (balls)
- Sample size indicator: HIGH (100+), MEDIUM (30-99), LOW (<30)

#### Section E: vs Teams (Top/Bottom 3)

**Display Format:**
```
vs TEAMS
Best:  MI (SR 168.4, 3 inns) | SRH (SR 162.1, 5 inns)
Worst: DC (SR 118.2, 4 inns) | GT (SR 124.5, 3 inns)
```

**Logic:**
- Sort by Strike Rate (descending) for Top 3
- Sort by Strike Rate (ascending) for Bottom 3
- Minimum 2 innings to qualify
- Show team abbreviation + SR + innings count

#### Section F: Entry Point Analysis

**Display Format:**
```
Entry Point: TOP_ORDER
Avg Entry: Ball 2.6 | Range: 1-13
Median Entry: Ball 1
```

**Classifications:**
| Classification | Avg Entry Ball |
|----------------|----------------|
| TOP_ORDER | <= 6 |
| MIDDLE_ORDER | 7-40 |
| FINISHER | > 40 |

---

### 5.2 BOWLER Profile Sections

#### Section A: Career Stats (IPL 2023+)

**Display Format:**
```
CAREER STATS (IPL 2023+)
Wickets: 47 | Economy: 6.97 | Avg: 18.4 | SR: 15.8
Overs: 124.2 | Dot%: 48.2% | Boundary%: 12.1%
```

**Metrics:**
| Metric | Formula | Source |
|--------|---------|--------|
| Wickets | COUNT(is_wicket = TRUE) | fact_ball |
| Overs | balls / 6 | Derived |
| Runs Conceded | SUM(total_runs) | fact_ball |
| Economy | (runs / balls) * 6 | Derived |
| Average | runs / wickets | Derived |
| Strike Rate | balls / wickets | Derived |
| Dot Ball % | dots / balls * 100 | fact_ball |
| Boundary % | (4s + 6s) / balls * 100 | fact_ball |

#### Section B: Phase Performance

**Display Format:**
```
PHASE PERFORMANCE
         Econ    Wkts    SR      Overs
PP:      6.14    16      11.1    44.2
Middle:  6.89    19      17.5    52.0
Death:   7.84    12      16.3    28.0
```

**Metrics per Phase:**
| Metric | PP | Middle | Death |
|--------|-----|--------|-------|
| Economy | pp_economy | mid_economy | death_economy |
| Wickets | pp_wickets | mid_wickets | death_wickets |
| Strike Rate | pp_sr | mid_sr | death_sr |
| Overs | pp_overs | mid_overs | death_overs |

#### Section C: Role Tags

**Display Format:**
```
ROLE TAGS
[PP_CONTAINER] [DEATH_COMPLETE] [MIDDLE_STRANGLER]
[LHB_WICKET_TAKER]
```

**Tag Categories:**
| Tag Type | Color | Examples |
|----------|-------|----------|
| Phase Strength | Green (#22C55E) | PP_STRIKE, DEATH_COMPLETE |
| Phase Weakness | Red (#EF4444) | PP_LIABILITY, DEATH_LIABILITY |
| Handedness | Blue (#3B82F6) | LHB_SPECIALIST, RHB_SPECIALIST |

#### Section D: vs Batting Hand Matchups

**Display Format:**
```
vs BATTING HAND
         Econ    SR      Wkts    Balls
vs LHB:  6.14    11.1    16      177
vs RHB:  6.99    17.5    19      333
```

**Handedness Tags:**
| Tag | Condition |
|-----|-----------|
| LHB_SPECIALIST | Economy vs LHB < 8.0 AND significantly better than RHB |
| RHB_SPECIALIST | Economy vs RHB < 8.0 AND significantly better than LHB |
| LHB_VULNERABLE | Economy vs LHB > 10.0 OR significantly worse than RHB |
| RHB_VULNERABLE | Economy vs RHB > 10.0 OR significantly worse than LHB |

#### Section E: vs Teams (Top/Bottom 3)

**Display Format:**
```
vs TEAMS
Best:  MI (Eco 5.84, 12 overs) | SRH (Eco 6.21, 8 overs)
Worst: DC (Eco 9.42, 6 overs) | GT (Eco 8.87, 10 overs)
```

**Logic:**
- Sort by Economy (ascending) for Top 3
- Sort by Economy (descending) for Bottom 3
- Minimum 18 balls (3 overs) to qualify

#### Section F: Bowler Classification

**Display Format:**
```
Classification: Right-arm Fast
Type: Lead Pacer
Archetype: POWERPLAY ASSASSIN
```

**Classifications:**
| Classification | Source |
|----------------|--------|
| Bowling Arm | `ipl_2026_squads.bowling_arm` |
| Bowling Type | `ipl_2026_squads.bowling_type` |
| Role Type | Derived from phase distribution |
| Archetype | K-means cluster label |

---

## 6. Technical Approach

### 6.1 Data Fetching Strategy

**Option A: Pre-computed JSON (Recommended)**
```
/outputs/player_profiles/
  - player_profiles_2023.json     # Master file
  - batters/
    - {player_id}.json            # Individual files
  - bowlers/
    - {player_id}.json
```

**JSON Structure:**
```json
{
  "player_id": "ba607b88",
  "player_name": "V Kohli",
  "team_name": "Royal Challengers Bengaluru",
  "role": "Batter",
  "price_cr": 21.0,
  "acquisition_type": "Retained",
  "archetype": "Elite Top-Order",
  "player_type": "batter",

  "career_stats": {
    "runs": 1483,
    "innings": 44,
    "balls_faced": 1011,
    "average": 48.8,
    "strike_rate": 146.6,
    "fifties": 12,
    "hundreds": 1,
    "fours": 142,
    "sixes": 45,
    "boundary_pct": 18.4,
    "dot_ball_pct": 32.1
  },

  "phase_performance": {
    "powerplay": {
      "sr": 143.2, "avg": 52.3, "boundary_pct": 21.2, "balls": 342
    },
    "middle": {
      "sr": 148.7, "avg": 46.1, "boundary_pct": 17.8, "balls": 456
    },
    "death": {
      "sr": 156.3, "avg": 41.2, "boundary_pct": 19.4, "balls": 213
    }
  },

  "tags": [
    "SPECIALIST_VS_PACE",
    "VULNERABLE_VS_SPIN",
    "VULNERABLE_VS_OFF_SPIN",
    "AGGRESSIVE"
  ],

  "vs_bowling_type": {
    "pace": { "sr": 152.3, "avg": 54.2, "balls": 580 },
    "spin": { "sr": 138.4, "avg": 41.1, "balls": 431 },
    "off_spin": { "sr": 129.7, "avg": 32.8, "balls": 198 },
    "leg_spin": { "sr": 142.1, "avg": 48.3, "balls": 167 },
    "left_arm_spin": { "sr": 145.6, "avg": 43.2, "balls": 66 }
  },

  "vs_teams": {
    "best": [
      { "team": "MI", "sr": 168.4, "innings": 3 },
      { "team": "SRH", "sr": 162.1, "innings": 5 }
    ],
    "worst": [
      { "team": "DC", "sr": 118.2, "innings": 4 },
      { "team": "GT", "sr": 124.5, "innings": 3 }
    ]
  },

  "entry_point": {
    "classification": "TOP_ORDER",
    "avg_entry_ball": 2.6,
    "median_entry_ball": 1,
    "min_entry": 1,
    "max_entry": 13,
    "innings": 44
  }
}
```

### 6.2 Modal Implementation

**React/Next.js Pseudocode:**
```jsx
// PlayerProfileModal.jsx
function PlayerProfileModal({ playerId, isOpen, onClose }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen && playerId) {
      fetchPlayerProfile(playerId)
        .then(setProfile)
        .finally(() => setLoading(false));
    }
  }, [playerId, isOpen]);

  if (!isOpen) return null;

  return (
    <Modal onClose={onClose}>
      {loading ? <Spinner /> : (
        <>
          <PlayerHeader profile={profile} />
          <CareerStats stats={profile.career_stats} />
          <PhasePerformance phases={profile.phase_performance} />
          <RoleTags tags={profile.tags} />
          {profile.player_type === 'batter'
            ? <BatterMatchups profile={profile} />
            : <BowlerMatchups profile={profile} />
          }
        </>
      )}
    </Modal>
  );
}
```

### 6.3 Performance Considerations

| Consideration | Solution |
|---------------|----------|
| Initial load time | Pre-compute all profiles at build time |
| Bundle size | Lazy-load modal component |
| Memory usage | Load only clicked player's data |
| Cache strategy | Cache profiles in session storage |
| Fallback | Show "Limited data available" for unclustered players |

### 6.4 Data Pipeline

```
scripts/generators/generate_player_profiles.py
  |
  v
outputs/player_profiles/
  - player_profiles_2023.json (master)
  - by_team/
    - rcb_profiles.json
    - mi_profiles.json
    ...
```

---

## 7. Dependencies

### 7.1 Required Tickets/Epics (All Complete)

| Dependency | Status | Owner |
|------------|--------|-------|
| Player Tags Generation | Complete | Stephen Curry |
| Player Clustering (K-means) | Complete | Stephen Curry |
| Phase Performance Views | Complete | Brock Purdy |
| Entry Point Analysis | Complete | Andy Flower |
| Bowling Type Matchups | Complete | Stephen Curry |
| Handedness Matchups | Complete | Stephen Curry |
| IPL 2026 Squad Data | Complete | Brock Purdy |

### 7.2 Data Availability

| Data Type | Available | Source |
|-----------|-----------|--------|
| Career Stats (2023+) | Yes | DuckDB views |
| Phase Performance | Yes | DuckDB views |
| Tags | Yes | `player_tags_2023.json` |
| Clusters | Yes | `player_clustering_2023.csv` |
| Entry Points | Yes | `batter_entry_points_2023.csv` |
| vs Bowling Type | Yes | `batter_bowling_type_*_2023.csv` |
| vs Handedness | Yes | `bowler_handedness_matchup_2023.csv` |
| vs Teams | Yes | DuckDB views |
| Squad/Contract | Yes | `ipl_2026_squads` |

### 7.3 Frontend Dependencies

| Dependency | Purpose | Status |
|------------|---------|--------|
| Modal Component | Display overlay | TBD |
| Tag/Badge Component | Display role tags | TBD |
| Table Component | Display stats | TBD |
| Click Handler | Player name interaction | TBD |

---

## 8. Success Metrics

### 8.1 Qualitative Success

| Criteria | Measurement |
|----------|-------------|
| Comprehensiveness | All requested data fields present |
| Conciseness | Profile scannable in <10 seconds |
| Cricket Validity | Andy Flower approval on metrics/tags |
| Usability | User can find key insights quickly |
| Consistency | Same structure for all players |

### 8.2 Quantitative Success (Post-Launch)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Modal Open Rate | >30% of team page visitors | Analytics |
| Time to Close | <30 seconds avg | Analytics |
| Repeat Opens | >2 per session | Analytics |
| Error Rate | <1% | Error tracking |
| Load Time | <500ms | Performance monitoring |

### 8.3 User Feedback Criteria

- "I understand this player's role and value"
- "I know when to bowl/bat this player"
- "I can see matchup advantages/vulnerabilities"
- "This is information I couldn't easily find elsewhere"

---

## 9. Task Breakdown

### 9.1 Suggested Tickets for This EPIC

| Ticket ID | Title | Estimate | Owner |
|-----------|-------|----------|-------|
| PPV-001 | Create player profile JSON schema | S | Brock Purdy |
| PPV-002 | Generate player profiles for batters | M | Brock Purdy |
| PPV-003 | Generate player profiles for bowlers | M | Brock Purdy |
| PPV-004 | Generate player profiles for all-rounders | M | Brock Purdy |
| PPV-005 | Implement PlayerProfileModal component | M | Frontend |
| PPV-006 | Implement click handler on player names | S | Frontend |
| PPV-007 | Style role tags with color coding | S | Frontend |
| PPV-008 | Add mobile responsive styles | S | Frontend |
| PPV-009 | Add loading/error states | S | Frontend |
| PPV-010 | Cricket domain review (Andy Flower) | S | Andy Flower |
| PPV-011 | Integration testing | M | N'Golo Kante |
| PPV-012 | Performance optimization | S | Frontend |

### 9.2 Ticket Sequencing

```
Phase 1: Data (PPV-001, PPV-002, PPV-003, PPV-004)
    |
    v
Phase 2: Frontend (PPV-005, PPV-006, PPV-007, PPV-008, PPV-009)
    |
    v
Phase 3: Review (PPV-010, PPV-011, PPV-012)
```

### 9.3 Effort Estimates

| Size | Tickets | Total |
|------|---------|-------|
| Small (S) | PPV-001, 006, 007, 008, 009, 010, 012 | 7 tickets |
| Medium (M) | PPV-002, 003, 004, 005, 011 | 5 tickets |

**Total Estimated Effort:** Medium-Large (5-7 days)

---

## 10. Approval Chain

### 10.1 Florentino Gate (Required First)

**Question:** Does this task materially improve the paid artifact or strategic decision?

**Analysis:**
- **Removes preparation burden:** Yes - users don't need external research
- **Improves decision-making:** Yes - clear matchup data for fantasy/analysis
- **Uses existing data:** Yes - all data already generated, just needs surfacing
- **Improves product stickiness:** Yes - interactive element keeps users engaged
- **Differentiator:** Yes - this depth of player data in one click is uncommon

**Recommendation:** APPROVE - This is core product functionality that surfaces existing data investment.

**Florentino Gate Status:** [X] APPROVED / [ ] ANALYTICS ONLY / [ ] NOT APPROVED

**Florentino Perez Review Date:** 2026-02-13

**Comments:** Core product functionality that surfaces existing data investment at zero marginal cost. All data already generated (tags, clusters, matchups, entry points). Founder-mandated feature. APPROVED.

---

### 10.2 Domain Sanity Loop

| Agent | Question | Answer | Date |
|-------|----------|--------|------|
| Jose Mourinho | Robust? Baselines clear? Scalable? | TBD | |
| Andy Flower | Makes sense to coach/analyst/fan? | TBD | |
| Pep Guardiola | Structurally coherent? | TBD | |

---

### 10.3 Founder Review (Required After Florentino Gate)

**Founder Review Status:** [ ] APPROVED / [ ] CHANGES REQUIRED / [ ] NOT APPROVED

**Founder Review Date:** ___________

**Comments:**

---

### 10.4 Enforcement Check

**Tom Brady:** [ ] PASS / [ ] FAIL

**Issues (if any):**

**Date:** ___________

---

### 10.5 System Check

**N'Golo Kante:** [ ] PASS / [ ] FAIL

**Tests:** [ ] All passing
**Schema:** [ ] Intact
**Manifests:** [ ] Updated

**Date:** ___________

---

## Appendix A: Sample Player Profiles

### Batter Example: Virat Kohli

```json
{
  "player_id": "ba607b88",
  "player_name": "V Kohli",
  "team_name": "Royal Challengers Bengaluru",
  "role": "Batter",
  "price_cr": 21.0,
  "acquisition_type": "Retained",
  "archetype": "Elite Top-Order",
  "player_type": "batter",
  "tags": ["SPECIALIST_VS_PACE", "VULNERABLE_VS_SPIN", "AGGRESSIVE"],
  "entry_point": {
    "classification": "TOP_ORDER",
    "avg_entry_ball": 2.6
  }
}
```

### Bowler Example: Jasprit Bumrah

```json
{
  "player_id": "462411b3",
  "player_name": "JJ Bumrah",
  "team_name": "Mumbai Indians",
  "role": "Bowler",
  "price_cr": 18.0,
  "acquisition_type": "Retained",
  "archetype": "Powerplay Assassin",
  "player_type": "bowler",
  "bowling_classification": {
    "arm": "Right-arm",
    "type": "Fast"
  },
  "tags": ["PP_CONTAINER", "DEATH_COMPLETE", "MIDDLE_STRANGLER", "LHB_WICKET_TAKER"]
}
```

---

## Appendix B: Tag Reference

### Batter Tags

| Tag | Meaning | Criteria |
|-----|---------|----------|
| SPECIALIST_VS_PACE | Excels against pace | SR >= 140 vs pace, 100+ balls |
| SPECIALIST_VS_SPIN | Excels against spin | SR >= 140 vs spin, 100+ balls |
| VULNERABLE_VS_PACE | Struggles against pace | SR <= 120 vs pace, 50+ balls |
| VULNERABLE_VS_SPIN | Struggles against spin | SR <= 120 vs spin, 50+ balls |
| SPECIALIST_VS_OFF_SPIN | Specific spin strength | SR >= 145 vs off-spin |
| SPECIALIST_VS_LEG_SPIN | Specific spin strength | SR >= 145 vs leg-spin |
| PP_DOMINATOR | Elite in powerplay | Elite in 3+ PP metrics |
| DEATH_FINISHER | Elite at death | Death SR >= 180, 30+ balls |
| PLAYMAKER | Balanced performer | High avg + moderate SR |
| SIX_HITTER | Power hitter | Six% >= 8% |
| AGGRESSIVE | High intent | SR >= 145 overall |

### Bowler Tags

| Tag | Meaning | Criteria |
|-----|---------|----------|
| PP_STRIKE | Wicket-taker in PP | W/B >= 0.05 in PP |
| PP_CONTAINER | Economical in PP | Economy <= 7.5 in PP |
| MIDDLE_STRANGLER | Dominates middle | Economy <= 7.0 in middle |
| DEATH_COMPLETE | Elite at death | Economy <= 9.5 AND W/B >= 0.08 |
| DEATH_STRIKE | Death wicket-taker | W/B >= 0.10 at death |
| LHB_SPECIALIST | Better vs LHB | Economy vs LHB < 8.0 |
| RHB_SPECIALIST | Better vs RHB | Economy vs RHB < 8.0 |
| LHB_VULNERABLE | Struggles vs LHB | Economy vs LHB > 10.5 |
| LHB_WICKET_TAKER | Takes LHB wickets | More LHB wickets than expected |

---

*Document Version: 1.0.0*
*Created: 2026-02-06*
*Author: Tom Brady (Product Owner)*
*Status: DRAFT - Awaiting Florentino Gate*

---

**TASK INTEGRITY LOOP:**

1. [X] Florentino Gate - APPROVED (2026-02-13)
2. [ ] Domain Sanity (Jose, Andy, Pep) - Pending (after Build)
3. [ ] Founder Review - Pending
4. [ ] Tom Brady Enforcement - Pending
5. [ ] N'Golo Kante System Check - Pending
