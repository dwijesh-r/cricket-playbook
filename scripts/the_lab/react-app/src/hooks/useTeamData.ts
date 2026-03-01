/**
 * Hook for fetching team roster and depth chart data from DuckDB-WASM.
 *
 * Queries the player_profiles and depth_chart tables for a given
 * team code and returns a structured team data result.
 *
 * @module hooks/useTeamData
 */

import { useMemo } from 'react';
import type {
  TeamCode,
  PlayerProfile,
  PlayerRole,
  BowlingStyle,
  DepthChartEntry,
} from '../types';
import { useSQLQuery } from './useSQLQuery';

/** Raw player row from the roster query */
interface RosterRow extends Record<string, unknown> {
  player_id: string;
  player_name: string;
  team: string;
  role: string;
  batting_style: string | null;
  bowling_style: string | null;
  matches: number;
  innings: number;
}

/** Raw depth chart row */
interface DepthChartRow extends Record<string, unknown> {
  team: string;
  role: string;
  slot: number;
  player_name: string;
  confidence: number;
}

/** Complete team data result */
export interface TeamData {
  /** Team franchise code */
  teamCode: TeamCode;
  /** Full player roster */
  roster: PlayerProfile[];
  /** Depth chart entries sorted by role and slot */
  depthChart: DepthChartEntry[];
  /** Roster grouped by role for quick access */
  rosterByRole: Record<string, PlayerProfile[]>;
}

/** Return type for the useTeamData hook */
export interface UseTeamDataResult {
  /** The team data, or null while loading */
  team: TeamData | null;
  /** Whether the queries are currently executing */
  loading: boolean;
  /** Error encountered during data fetch, if any */
  error: Error | null;
  /** Manually re-fetch the team data */
  refetch: () => void;
}

/**
 * Escape a string for use in a SQL query.
 */
function escapeSQLString(value: string): string {
  return value.replace(/'/g, "''");
}

/**
 * Transform a raw row into a typed PlayerProfile.
 */
function toPlayerProfile(row: RosterRow): PlayerProfile {
  return {
    player_id: String(row.player_id),
    player_name: String(row.player_name),
    team: String(row.team) as TeamCode,
    role: String(row.role) as PlayerRole,
    batting_style: row.batting_style ? String(row.batting_style) : undefined,
    bowling_style: row.bowling_style
      ? (String(row.bowling_style) as BowlingStyle)
      : undefined,
    matches: Number(row.matches),
    innings: Number(row.innings),
  };
}

/**
 * Transform a raw row into a typed DepthChartEntry.
 */
function toDepthChartEntry(row: DepthChartRow): DepthChartEntry {
  return {
    team: String(row.team) as TeamCode,
    role: String(row.role),
    slot: Number(row.slot),
    player_name: String(row.player_name),
    confidence: Number(row.confidence),
  };
}

/**
 * Group roster players by their role.
 */
function groupByRole(
  roster: PlayerProfile[],
): Record<string, PlayerProfile[]> {
  const groups: Record<string, PlayerProfile[]> = {};
  for (const player of roster) {
    const role = player.role;
    if (!groups[role]) {
      groups[role] = [];
    }
    groups[role].push(player);
  }
  return groups;
}

/**
 * Hook that fetches a team's roster and depth chart by team code.
 *
 * Issues two parallel SQL queries (roster and depth chart) and merges
 * the results into a single structured TeamData object.
 *
 * @example
 * ```tsx
 * function TeamPage({ teamCode }: { teamCode: TeamCode }) {
 *   const { team, loading, error } = useTeamData(teamCode);
 *   if (loading) return <Spinner />;
 *   if (error) return <ErrorBanner error={error} />;
 *   if (!team) return <NotFound />;
 *   return (
 *     <div>
 *       <h1>{team.teamCode}</h1>
 *       <p>{team.roster.length} players</p>
 *     </div>
 *   );
 * }
 * ```
 *
 * @param teamCode - The IPL franchise code (e.g., 'CSK', 'MI')
 */
export function useTeamData(teamCode: TeamCode | null): UseTeamDataResult {
  const rosterQuery = useMemo(() => {
    if (!teamCode) return '';
    const safeCode = escapeSQLString(teamCode);
    return `
      SELECT
        player_id,
        player_name,
        team,
        role,
        batting_style,
        bowling_style,
        matches,
        innings
      FROM player_profiles
      WHERE team = '${safeCode}'
      ORDER BY role, player_name
    `.trim();
  }, [teamCode]);

  const depthChartQuery = useMemo(() => {
    if (!teamCode) return '';
    const safeCode = escapeSQLString(teamCode);
    return `
      SELECT
        team,
        role,
        slot,
        player_name,
        confidence
      FROM depth_chart
      WHERE team = '${safeCode}'
      ORDER BY role, slot
    `.trim();
  }, [teamCode]);

  const rosterResult = useSQLQuery<RosterRow>({
    query: rosterQuery,
    enabled: !!teamCode,
    key: teamCode ?? undefined,
  });

  const depthChartResult = useSQLQuery<DepthChartRow>({
    query: depthChartQuery,
    enabled: !!teamCode,
    key: teamCode ? `depth-${teamCode}` : undefined,
  });

  const loading = rosterResult.loading || depthChartResult.loading;
  const error = rosterResult.error ?? depthChartResult.error;

  const team = useMemo((): TeamData | null => {
    if (!teamCode) return null;
    if (!rosterResult.data) return null;

    const roster = rosterResult.data.map(toPlayerProfile);
    const depthChart = (depthChartResult.data ?? []).map(toDepthChartEntry);
    const rosterByRole = groupByRole(roster);

    return {
      teamCode,
      roster,
      depthChart,
      rosterByRole,
    };
  }, [teamCode, rosterResult.data, depthChartResult.data]);

  const refetch = useMemo(() => {
    return () => {
      rosterResult.refetch();
      depthChartResult.refetch();
    };
  }, [rosterResult, depthChartResult]);

  return { team, loading, error, refetch };
}
