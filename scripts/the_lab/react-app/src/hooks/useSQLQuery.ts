/**
 * Generic SQL query hook for DuckDB-WASM.
 *
 * Executes arbitrary SQL against the DuckDB instance and returns typed
 * results with loading/error states. Memoizes the query string to prevent
 * unnecessary re-execution on re-renders.
 *
 * @module hooks/useSQLQuery
 */

import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { executeQuery } from '../data/duckdb';

/** Options for the useSQLQuery hook */
export interface UseSQLQueryOptions {
  /** The SQL query to execute */
  query: string;
  /** Whether the query should execute. Defaults to true. */
  enabled?: boolean;
  /**
   * Dependency key — when this changes, the query re-executes.
   * Useful for parameterized queries where the SQL string changes.
   */
  key?: string;
}

/** Return type for the useSQLQuery hook */
export interface UseSQLQueryResult<T> {
  /** The query result rows, or null if not yet loaded */
  data: T[] | null;
  /** Whether the query is currently executing */
  loading: boolean;
  /** Error encountered during query execution, if any */
  error: Error | null;
  /** Manually re-execute the query */
  refetch: () => void;
}

/**
 * Hook that executes a SQL query against DuckDB-WASM and returns typed results.
 *
 * The query is memoized so that identical query strings do not trigger
 * re-execution. Use the `enabled` flag to conditionally run queries
 * and the `key` option to force re-execution when parameters change.
 *
 * @example
 * ```tsx
 * function PlayerList() {
 *   const { data, loading, error } = useSQLQuery<{ name: string }>({
 *     query: "SELECT player_name as name FROM players WHERE team = 'CSK'",
 *   });
 *
 *   if (loading) return <Spinner />;
 *   if (error) return <ErrorBanner error={error} />;
 *   return <ul>{data?.map(p => <li key={p.name}>{p.name}</li>)}</ul>;
 * }
 * ```
 *
 * @typeParam T - The expected row shape of the query result
 */
export function useSQLQuery<T extends Record<string, unknown>>(
  options: UseSQLQueryOptions,
): UseSQLQueryResult<T> {
  const { query, enabled = true, key } = options;

  const [data, setData] = useState<T[] | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const [fetchCount, setFetchCount] = useState<number>(0);
  const mountedRef = useRef<boolean>(true);

  // Memoize the query string to prevent re-execution on identical queries
  const stableQuery = useMemo(() => query, [query]);

  // Memoize the dependency key
  const stableKey = useMemo(() => key, [key]);

  const refetch = useCallback(() => {
    setFetchCount((prev) => prev + 1);
  }, []);

  useEffect(() => {
    mountedRef.current = true;

    if (!enabled) {
      setData(null);
      setLoading(false);
      setError(null);
      return;
    }

    let cancelled = false;

    async function run(): Promise<void> {
      setLoading(true);
      setError(null);

      try {
        const rows = await executeQuery<T>(stableQuery);
        if (!cancelled && mountedRef.current) {
          setData(rows);
          setLoading(false);
        }
      } catch (err) {
        if (!cancelled && mountedRef.current) {
          setError(
            err instanceof Error
              ? err
              : new Error(`SQL query failed: ${String(err)}`),
          );
          setData(null);
          setLoading(false);
        }
      }
    }

    void run();

    return () => {
      cancelled = true;
      mountedRef.current = false;
    };
  }, [stableQuery, stableKey, enabled, fetchCount]);

  return { data, loading, error, refetch };
}
