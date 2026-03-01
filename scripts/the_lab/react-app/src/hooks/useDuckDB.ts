/**
 * React hook providing access to the DuckDB-WASM singleton instance.
 *
 * Lazy-initializes DuckDB on first use and exposes loading/error states
 * so components can render appropriate UI during initialization.
 *
 * @module hooks/useDuckDB
 */

import { useState, useEffect, useRef } from 'react';
import type * as duckdb from '@duckdb/duckdb-wasm';
import { getDB } from '../data/duckdb';

/** Return type for the useDuckDB hook */
export interface UseDuckDBResult {
  /** The initialized DuckDB instance, or null while loading */
  db: duckdb.AsyncDuckDB | null;
  /** Whether the DuckDB instance is currently being initialized */
  loading: boolean;
  /** Error encountered during initialization, if any */
  error: Error | null;
}

/**
 * Hook that provides the DuckDB-WASM instance with lifecycle management.
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { db, loading, error } = useDuckDB();
 *   if (loading) return <Spinner />;
 *   if (error) return <ErrorBanner error={error} />;
 *   // Use db...
 * }
 * ```
 */
export function useDuckDB(): UseDuckDBResult {
  const [db, setDb] = useState<duckdb.AsyncDuckDB | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const mountedRef = useRef<boolean>(true);

  useEffect(() => {
    mountedRef.current = true;

    let cancelled = false;

    async function init(): Promise<void> {
      try {
        const instance = await getDB();
        if (!cancelled && mountedRef.current) {
          setDb(instance);
          setLoading(false);
        }
      } catch (err) {
        if (!cancelled && mountedRef.current) {
          setError(
            err instanceof Error
              ? err
              : new Error(`DuckDB init failed: ${String(err)}`),
          );
          setLoading(false);
        }
      }
    }

    void init();

    return () => {
      cancelled = true;
      mountedRef.current = false;
    };
  }, []);

  return { db, loading, error };
}
