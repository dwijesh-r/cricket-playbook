/**
 * Barrel export for all React hooks used by the Statsledge dashboard.
 *
 * @module hooks
 */

export { useTheme } from './useTheme';
export { useDuckDB } from './useDuckDB';
export { useSQLQuery } from './useSQLQuery';
export { usePlayerData } from './usePlayerData';
export { useComparisonData } from './useComparisonData';
export { useTeamData } from './useTeamData';

// Re-export hook result types for consumer convenience
export type { UseDuckDBResult } from './useDuckDB';
export type { UseSQLQueryOptions, UseSQLQueryResult } from './useSQLQuery';
export type { UsePlayerDataResult } from './usePlayerData';
export type {
  UseComparisonDataResult,
  PlayerComparisonStats,
} from './useComparisonData';
export type { UseTeamDataResult, TeamData } from './useTeamData';
