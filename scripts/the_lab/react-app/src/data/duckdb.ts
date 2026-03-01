/**
 * DuckDB-WASM initialization module for Statsledge.
 *
 * Provides a singleton DuckDB instance that lazy-loads on first use.
 * The database file path is configurable via VITE_DUCKDB_DATA_URL
 * environment variable — in production this points to a CDN-hosted
 * parquet/database file; in development it defaults to a local path.
 *
 * @module data/duckdb
 */

import * as duckdb from '@duckdb/duckdb-wasm';

/** Configuration for DuckDB data source */
export interface DuckDBConfig {
  /** Base URL where database/parquet files are served from */
  dataBaseUrl: string;
  /** Database filename to load (relative to dataBaseUrl) */
  databaseFile: string;
}

const DEFAULT_CONFIG: DuckDBConfig = {
  dataBaseUrl: import.meta.env.VITE_DUCKDB_DATA_URL ?? '/data',
  databaseFile: import.meta.env.VITE_DUCKDB_FILE ?? 'cricket_playbook.duckdb',
};

/** DuckDB initialization state */
interface DuckDBState {
  db: duckdb.AsyncDuckDB | null;
  connection: duckdb.AsyncDuckDBConnection | null;
  initializing: boolean;
  error: Error | null;
}

const state: DuckDBState = {
  db: null,
  connection: null,
  initializing: false,
  error: null,
};

/** Pending initialization promise to avoid duplicate init calls */
let initPromise: Promise<duckdb.AsyncDuckDB> | null = null;

/**
 * Select the best available DuckDB-WASM bundle for the current browser.
 * Prefers the EH (exception handling) bundle when available.
 */
async function selectBundle(): Promise<duckdb.DuckDBBundles> {
  const JSDELIVR_BUNDLES = duckdb.getJsDelivrBundles();

  const bundle = await duckdb.selectBundle(JSDELIVR_BUNDLES);

  if (!bundle.mainWorker) {
    throw new Error(
      'DuckDB-WASM: No compatible worker bundle found for this browser.',
    );
  }

  return {
    mainModule: bundle.mainModule,
    mainWorker: bundle.mainWorker,
    pthreadWorker: bundle.pthreadWorker,
  };
}

/**
 * Initialize the DuckDB-WASM instance. This is idempotent — calling it
 * multiple times returns the same singleton promise.
 */
async function initializeDuckDB(
  config: DuckDBConfig = DEFAULT_CONFIG,
): Promise<duckdb.AsyncDuckDB> {
  if (state.db) {
    return state.db;
  }

  if (state.error) {
    throw state.error;
  }

  if (initPromise) {
    return initPromise;
  }

  state.initializing = true;

  initPromise = (async () => {
    try {
      const bundles = await selectBundle();

      const worker = new Worker(bundles.mainWorker!);
      const logger = new duckdb.ConsoleLogger(duckdb.LogLevel.WARNING);
      const db = new duckdb.AsyncDuckDB(logger, worker);

      await db.instantiate(bundles.mainModule, bundles.pthreadWorker);

      // Register the remote database file so queries can access it
      const databaseUrl = `${config.dataBaseUrl}/${config.databaseFile}`;
      await db.registerFileURL(
        config.databaseFile,
        databaseUrl,
        duckdb.DuckDBDataProtocol.HTTP,
        false,
      );

      state.db = db;
      state.error = null;
      state.initializing = false;

      return db;
    } catch (err) {
      const error =
        err instanceof Error
          ? err
          : new Error(`DuckDB initialization failed: ${String(err)}`);
      state.error = error;
      state.initializing = false;
      initPromise = null;
      throw error;
    }
  })();

  return initPromise;
}

/**
 * Get (or create) the singleton DuckDB instance.
 *
 * @param config - Optional configuration override
 * @returns The initialized AsyncDuckDB instance
 */
export async function getDB(
  config?: DuckDBConfig,
): Promise<duckdb.AsyncDuckDB> {
  return initializeDuckDB(config ?? DEFAULT_CONFIG);
}

/**
 * Get a connection to the DuckDB instance.
 * Reuses a single connection to avoid overhead.
 *
 * @returns An open DuckDB connection
 */
export async function getConnection(): Promise<duckdb.AsyncDuckDBConnection> {
  if (state.connection) {
    return state.connection;
  }

  const db = await getDB();
  const conn = await db.connect();
  state.connection = conn;
  return conn;
}

/**
 * Execute a SQL query and return the results as an array of typed objects.
 *
 * @param sql - The SQL query string
 * @param params - Optional query parameters
 * @returns Array of result rows
 */
export async function executeQuery<T extends Record<string, unknown>>(
  sql: string,
): Promise<T[]> {
  const conn = await getConnection();
  const result = await conn.query(sql);

  const rows: T[] = [];
  const batches = result.batches;

  for (const batch of batches) {
    const numRows = batch.numRows;
    for (let i = 0; i < numRows; i++) {
      const row: Record<string, unknown> = {};
      for (const field of result.schema.fields) {
        const column = batch.getChild(field.name);
        row[field.name] = column?.get(i);
      }
      rows.push(row as T);
    }
  }

  return rows;
}

/**
 * Reset the DuckDB singleton. Useful for testing or error recovery.
 */
export async function resetDB(): Promise<void> {
  if (state.connection) {
    await state.connection.close();
    state.connection = null;
  }

  if (state.db) {
    await state.db.terminate();
    state.db = null;
  }

  state.error = null;
  state.initializing = false;
  initPromise = null;
}
