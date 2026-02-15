/**
 * Data loading utilities for the Cricket Playbook React Dashboard.
 *
 * The existing Lab dashboard uses .js files that assign data to global
 * variables (e.g., `const COMPARISON_DATA = {...}`). For the React app,
 * we will eventually either:
 * 1. Import these files directly and parse the global assignments, or
 * 2. Generate parallel .json files from the Python pipeline.
 *
 * For now, this module provides the interface that future data loaders
 * will implement.
 */

const DATA_BASE_URL = '../dashboard/data';

/**
 * Load a JSON data file from the data directory.
 * Future implementation will fetch from the generated data files.
 */
export async function loadDataFile<T>(filename: string): Promise<T> {
  const url = `${DATA_BASE_URL}/${filename}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to load data file: ${filename} (${response.status})`);
  }
  return response.json() as Promise<T>;
}

/**
 * Check if a data file exists and is accessible.
 */
export async function checkDataAvailability(filename: string): Promise<boolean> {
  try {
    const url = `${DATA_BASE_URL}/${filename}`;
    const response = await fetch(url, { method: 'HEAD' });
    return response.ok;
  } catch {
    return false;
  }
}
