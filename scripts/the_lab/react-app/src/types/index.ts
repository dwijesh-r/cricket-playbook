/**
 * Core type definitions for Cricket Playbook React Dashboard.
 *
 * These types mirror the data structures produced by the Python analytics
 * pipeline (analytics_ipl.py) and exposed via the dashboard/data/*.js files.
 */

/** IPL team identifiers (franchise codes) */
export type TeamCode =
  | 'CSK'
  | 'MI'
  | 'RCB'
  | 'KKR'
  | 'DC'
  | 'PBKS'
  | 'RR'
  | 'SRH'
  | 'GT'
  | 'LSG';

/** Player role classification */
export type PlayerRole = 'Batter' | 'Bowler' | 'All-rounder' | 'Wicket-keeper';

/** Bowling style classification */
export type BowlingStyle = 'Pace' | 'Medium' | 'Off-spin' | 'Leg-spin' | 'Left-arm spin';

/** Match phase */
export type Phase = 'powerplay' | 'middle' | 'death';

/** Base player profile from player_profiles.js */
export interface PlayerProfile {
  player_id: string;
  player_name: string;
  team: TeamCode;
  role: PlayerRole;
  batting_style?: string;
  bowling_style?: BowlingStyle;
  matches: number;
  innings: number;
}

/** Comparison metric for the comparison tool */
export interface ComparisonMetric {
  metric_name: string;
  player_a_value: number;
  player_b_value: number;
  unit: string;
  higher_is_better: boolean;
}

/** Win probability data point */
export interface WinProbDataPoint {
  ball_number: number;
  over: number;
  ball_in_over: number;
  innings: 1 | 2;
  batting_team_win_prob: number;
  bowling_team_win_prob: number;
  runs_scored: number;
  wicket: boolean;
  commentary?: string;
}

/** Match summary for win probability viewer */
export interface MatchSummary {
  match_id: string;
  date: string;
  venue: string;
  team_a: TeamCode;
  team_b: TeamCode;
  winner: TeamCode;
  margin: string;
  season: number;
}

/** Team depth chart entry */
export interface DepthChartEntry {
  team: TeamCode;
  role: string;
  slot: number;
  player_name: string;
  confidence: number;
}

/** Theme type */
export type Theme = 'dark' | 'light';
