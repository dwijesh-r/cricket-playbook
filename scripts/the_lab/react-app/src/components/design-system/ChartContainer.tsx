import { forwardRef, type HTMLAttributes, type ReactNode } from 'react';
import styles from './ChartContainer.module.css';

export interface ChartContainerProps extends HTMLAttributes<HTMLDivElement> {
  /** Chart title displayed in the header */
  title: string;
  /** Optional subtitle / description */
  subtitle?: string;
  /** Chart content */
  children: ReactNode;
  /** Show skeleton loading state */
  loading?: boolean;
  /** Remove horizontal padding for edge-to-edge charts */
  fullWidth?: boolean;
}

export const ChartContainer = forwardRef<HTMLDivElement, ChartContainerProps>(
  ({ title, subtitle, children, loading = false, fullWidth = false, className, ...rest }, ref) => {
    const cls = [
      styles.container,
      fullWidth ? styles.fullWidth : '',
      className,
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <div
        ref={ref}
        className={cls}
        role="figure"
        aria-label={title}
        aria-busy={loading}
        {...rest}
      >
        {/* Header */}
        <div className={styles.header}>
          <h3 className={styles.title}>{title}</h3>
          {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
        </div>

        {/* Body */}
        <div className={styles.body}>
          {loading ? (
            <div className={styles.skeleton} aria-label="Loading chart data">
              <div className={styles.skeletonBar} />
              <div className={styles.skeletonBar} />
              <div className={styles.skeletonBar} />
              <div className={styles.skeletonBar} />
              <div className={styles.skeletonBar} />
            </div>
          ) : (
            <div className={styles.loaded}>{children}</div>
          )}
        </div>
      </div>
    );
  },
);

ChartContainer.displayName = 'ChartContainer';

export default ChartContainer;
