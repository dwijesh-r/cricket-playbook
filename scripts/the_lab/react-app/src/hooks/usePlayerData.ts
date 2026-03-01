/**
 * Hook for fetching player profile data from DuckDB-WASM.
 *
 * Queries the players table for a specific player by ID and returns
 * a structured PlayerProfile result.
 *
 * @module hooks/usePlayerData
 */

import { useMemo } from 'react';
import type { PlayerProfile, PlayerRole, BowlingStyle, TeamCode } from '../types';
import { useSQLQuery } from './useSQLQuery';

/** Raw row shape returned by the player query */
interface PlayerRow extends Record<string, unknown> {
  player_id: string;
  player_name: string;
  team: string;
  role: string;
  batting_style: string | null;
  bowling_style: string | null;
  matches: number;
  innings: number;
}

/** Return type for the usePlayerData hook */
export interface UsePlayerDataResult {
  /** The player profile, or null if not loaded */
  player: PlayerProfile | null;
  /** Whether the query is currently executing */
  loading: boolean;
  /** Error encountered during data fetch, if any */
  error: Error | null;
  /** Manually re-fetch the player data */
  refetch: () => void;
}

/**
 * Escape a string for use in a SQL query to prevent injection.
 * Replaces single quotes with doubled single quotes.
 */
function escapeSQLString(value: string): string {
  return value.replace(/'/g, "''");
}

/**
 * Transform a raw database row into a typed PlayerProfile.
 */
function toPlayerProfile(row: PlayerRow): PlayerProfile {
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
 * Hook that fetches a player profile by player ID.
 *
 * @example
 * ```tsx
 * function PlayerCard({ playerId }: { playerId: string }) {
 *   const { player, loading, error } = usePlayerData(playerId);
 *   if (loading) return <Spinner />;
 *   if (error) return <ErrorBanner error={error} />;
 *   if (!player) return <NotFound />;
 *   return <div>{player.player_name} — {player.team}</div>;
 * }
 * ```
 *
 * @param playerId - The unique player identifier
 */
export function usePlayerData(playerId: string | null): UsePlayerDataResult {
  const query = useMemo(() => {
    if (!playerId) return '';
    const safeId = escapeSQLString(playerId);
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
      WHERE player_id = '${safeId}'
      LIMIT 1
    `.trim();
  }, [playerId]);

  const { data, loading, error, refetch } = useSQLQuery<PlayerRow>({
    query,
    enabled: !!playerId,
    key: playerId ?? undefined,
  });

  const player = useMemo(() => {
    if (!data || data.length === 0) return null;
    return toPlayerProfile(data[0]);
  }, [data]);

  return { player, loading, error, refetch };
}
