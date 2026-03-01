/**
 * Hook for fetching comparison data for two or more players.
 *
 * Queries DuckDB-WASM for key batting and bowling metrics across
 * the provided player IDs, returning structured comparison results
 * ready for the comparison tool UI.
 *
 * @module hooks/useComparisonData
 */

import { useMemo } from 'react';
import type { ComparisonMetric } from '../types';
import { useSQLQuery } from './useSQLQuery';

/** Raw row shape returned by the comparison query */
interface ComparisonRow extends Record<string, unknown> {
  player_id: string;
  player_name: string;
  matches: number;
  innings: number;
  runs: number;
  average: number;
  strike_rate: number;
  wickets: number;
  economy: number;
  bowling_average: number;
}

/** A single player's comparison stats */
export interface PlayerComparisonStats {
  playerId: string;
  playerName: string;
  metrics: Record<string, number>;
}

/** Return type for the useComparisonData hook */
export interface UseComparisonDataResult {
  /** Per-player stats for each requested player */
  players: PlayerComparisonStats[];
  /** Structured comparison metrics (pairwise for first two players) */
  metrics: ComparisonMetric[];
  /** Whether the query is currently executing */
  loading: boolean;
  /** Error encountered during data fetch, if any */
  error: Error | null;
  /** Manually re-fetch the comparison data */
  refetch: () => void;
}

/**
 * Escape a string for use in a SQL query.
 */
function escapeSQLString(value: string): string {
  return value.replace(/'/g, "''");
}

/** Metric definitions for the comparison tool */
interface MetricDefinition {
  name: string;
  field: string;
  unit: string;
  higherIsBetter: boolean;
}

const COMPARISON_METRICS: MetricDefinition[] = [
  { name: 'Matches', field: 'matches', unit: '', higherIsBetter: true },
  { name: 'Innings', field: 'innings', unit: '', higherIsBetter: true },
  { name: 'Runs', field: 'runs', unit: '', higherIsBetter: true },
  { name: 'Batting Average', field: 'average', unit: '', higherIsBetter: true },
  {
    name: 'Strike Rate',
    field: 'strike_rate',
    unit: '',
    higherIsBetter: true,
  },
  { name: 'Wickets', field: 'wickets', unit: '', higherIsBetter: true },
  { name: 'Economy', field: 'economy', unit: 'RPO', higherIsBetter: false },
  {
    name: 'Bowling Average',
    field: 'bowling_average',
    unit: '',
    higherIsBetter: false,
  },
];

/**
 * Build pairwise ComparisonMetric objects from two player rows.
 */
function buildComparisonMetrics(
  playerA: ComparisonRow,
  playerB: ComparisonRow,
): ComparisonMetric[] {
  return COMPARISON_METRICS.map((def) => ({
    metric_name: def.name,
    player_a_value: Number(playerA[def.field] ?? 0),
    player_b_value: Number(playerB[def.field] ?? 0),
    unit: def.unit,
    higher_is_better: def.higherIsBetter,
  }));
}

/**
 * Transform a raw row into PlayerComparisonStats.
 */
function toPlayerStats(row: ComparisonRow): PlayerComparisonStats {
  return {
    playerId: String(row.player_id),
    playerName: String(row.player_name),
    metrics: {
      matches: Number(row.matches ?? 0),
      innings: Number(row.innings ?? 0),
      runs: Number(row.runs ?? 0),
      average: Number(row.average ?? 0),
      strike_rate: Number(row.strike_rate ?? 0),
      wickets: Number(row.wickets ?? 0),
      economy: Number(row.economy ?? 0),
      bowling_average: Number(row.bowling_average ?? 0),
    },
  };
}

/**
 * Hook that fetches comparison data for multiple players.
 *
 * Requires at least 2 player IDs. The `metrics` field in the result
 * provides pairwise comparison for the first two players (matching
 * the ComparisonMetric type used by the comparison tool UI).
 *
 * @example
 * ```tsx
 * function ComparisonView({ ids }: { ids: string[] }) {
 *   const { players, metrics, loading, error } = useComparisonData(ids);
 *   if (loading) return <Spinner />;
 *   if (error) return <ErrorBanner error={error} />;
 *   return <ComparisonTable metrics={metrics} />;
 * }
 * ```
 *
 * @param playerIds - Array of player IDs to compare (minimum 2)
 */
export function useComparisonData(
  playerIds: string[],
): UseComparisonDataResult {
  const hasEnoughPlayers = playerIds.length >= 2;

  const query = useMemo(() => {
    if (!hasEnoughPlayers) return '';

    const safeIds = playerIds.map((id) => `'${escapeSQLString(id)}'`).join(',');

    return `
      SELECT
        player_id,
        player_name,
        matches,
        innings,
        COALESCE(runs, 0) as runs,
        COALESCE(average, 0) as average,
        COALESCE(strike_rate, 0) as strike_rate,
        COALESCE(wickets, 0) as wickets,
        COALESCE(economy, 0) as economy,
        COALESCE(bowling_average, 0) as bowling_average
      FROM player_profiles
      WHERE player_id IN (${safeIds})
    `.trim();
  }, [playerIds, hasEnoughPlayers]);

  const queryKey = useMemo(() => playerIds.sort().join(','), [playerIds]);

  const { data, loading, error, refetch } = useSQLQuery<ComparisonRow>({
    query,
    enabled: hasEnoughPlayers,
    key: queryKey,
  });

  const players = useMemo(() => {
    if (!data) return [];
    return data.map(toPlayerStats);
  }, [data]);

  const metrics = useMemo(() => {
    if (!data || data.length < 2) return [];
    return buildComparisonMetrics(data[0], data[1]);
  }, [data]);

  return { players, metrics, loading, error, refetch };
}
