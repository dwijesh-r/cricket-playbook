import { forwardRef, useCallback, type HTMLAttributes, type ChangeEvent } from 'react';
import styles from './FilterBar.module.css';

export interface FilterDefinition {
  /** Unique key for this filter */
  key: string;
  /** Display label */
  label: string;
  /** Dropdown options */
  options: string[];
  /** Currently selected value */
  value?: string;
}

export interface FilterBarProps extends Omit<HTMLAttributes<HTMLDivElement>, 'onChange'> {
  /** Filter definitions */
  filters: FilterDefinition[];
  /** Called when any filter value changes */
  onChange: (key: string, value: string) => void;
}

export const FilterBar = forwardRef<HTMLDivElement, FilterBarProps>(
  ({ filters, onChange, className, ...rest }, ref) => {
    const cls = [styles.bar, className].filter(Boolean).join(' ');

    const handleChange = useCallback(
      (key: string) => (e: ChangeEvent<HTMLSelectElement>) => {
        onChange(key, e.target.value);
      },
      [onChange],
    );

    return (
      <div
        ref={ref}
        className={cls}
        role="toolbar"
        aria-label="Filters"
        {...rest}
      >
        {filters.map((filter) => (
          <div key={filter.key} className={styles.filterGroup}>
            <label
              htmlFor={`filter-${filter.key}`}
              className={styles.label}
            >
              {filter.label}
            </label>
            <select
              id={`filter-${filter.key}`}
              className={styles.select}
              value={filter.value ?? ''}
              onChange={handleChange(filter.key)}
              aria-label={filter.label}
            >
              <option value="">All</option>
              {filter.options.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </div>
        ))}
      </div>
    );
  },
);

FilterBar.displayName = 'FilterBar';

export default FilterBar;
