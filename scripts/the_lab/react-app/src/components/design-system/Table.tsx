import { forwardRef, useState, useCallback, type HTMLAttributes } from 'react';
import styles from './Table.module.css';

export type SortDirection = 'asc' | 'desc';

export interface TableColumn {
  /** Unique key matching a property in the data objects */
  key: string;
  /** Display label */
  label: string;
  /** Whether the column is sortable */
  sortable?: boolean;
  /** Text alignment */
  align?: 'left' | 'center' | 'right';
}

export interface TableProps extends Omit<HTMLAttributes<HTMLDivElement>, 'children'> {
  /** Column definitions */
  columns: TableColumn[];
  /** Row data — each object should have keys matching column keys */
  data: Record<string, unknown>[];
  /** Called when a sortable column header is clicked */
  onSort?: (key: string, direction: SortDirection) => void;
  /** Message shown when data is empty */
  emptyMessage?: string;
}

const alignMap: Record<string, string> = {
  left: styles.alignLeft,
  center: styles.alignCenter,
  right: styles.alignRight,
};

export const Table = forwardRef<HTMLDivElement, TableProps>(
  ({ columns, data, onSort, emptyMessage = 'No data available', className, ...rest }, ref) => {
    const [sortKey, setSortKey] = useState<string | null>(null);
    const [sortDir, setSortDir] = useState<SortDirection>('asc');

    const handleSort = useCallback(
      (col: TableColumn) => {
        if (!col.sortable) return;
        const newDir: SortDirection =
          sortKey === col.key && sortDir === 'asc' ? 'desc' : 'asc';
        setSortKey(col.key);
        setSortDir(newDir);
        onSort?.(col.key, newDir);
      },
      [sortKey, sortDir, onSort],
    );

    // Internal sort when no external onSort is provided
    const sortedData = (() => {
      if (!sortKey) return data;
      if (onSort) return data; // external sort — trust caller's data order
      return [...data].sort((a, b) => {
        const aVal = a[sortKey];
        const bVal = b[sortKey];
        if (aVal == null && bVal == null) return 0;
        if (aVal == null) return 1;
        if (bVal == null) return -1;
        if (typeof aVal === 'number' && typeof bVal === 'number') {
          return sortDir === 'asc' ? aVal - bVal : bVal - aVal;
        }
        const aStr = String(aVal);
        const bStr = String(bVal);
        return sortDir === 'asc'
          ? aStr.localeCompare(bStr)
          : bStr.localeCompare(aStr);
      });
    })();

    const wrapperCls = [styles.wrapper, className].filter(Boolean).join(' ');

    return (
      <div ref={ref} className={wrapperCls} role="region" aria-label="Data table" tabIndex={0} {...rest}>
        <table className={styles.table}>
          <thead>
            <tr>
              {columns.map((col) => {
                const isActive = sortKey === col.key;
                const thCls = [
                  styles.th,
                  col.sortable ? styles.thSortable : '',
                  isActive ? styles.sortActive : '',
                  alignMap[col.align ?? 'left'],
                ]
                  .filter(Boolean)
                  .join(' ');

                return (
                  <th
                    key={col.key}
                    className={thCls}
                    onClick={() => handleSort(col)}
                    aria-sort={
                      isActive
                        ? sortDir === 'asc'
                          ? 'ascending'
                          : 'descending'
                        : col.sortable
                          ? 'none'
                          : undefined
                    }
                    scope="col"
                  >
                    {col.label}
                    {col.sortable && (
                      <span className={styles.sortIndicator} aria-hidden="true">
                        {isActive ? (sortDir === 'asc' ? '\u25B2' : '\u25BC') : '\u25B4'}
                      </span>
                    )}
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {sortedData.length === 0 ? (
              <tr>
                <td className={styles.empty} colSpan={columns.length}>
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              sortedData.map((row, idx) => (
                <tr key={idx} className={styles.row}>
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      className={[styles.td, alignMap[col.align ?? 'left']]
                        .filter(Boolean)
                        .join(' ')}
                    >
                      {row[col.key] != null ? String(row[col.key]) : '—'}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    );
  },
);

Table.displayName = 'Table';

export default Table;
