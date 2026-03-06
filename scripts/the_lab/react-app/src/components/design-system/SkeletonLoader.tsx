import { forwardRef, type HTMLAttributes } from 'react';
import styles from './SkeletonLoader.module.css';

export type SkeletonVariant = 'text' | 'card' | 'chart' | 'table';

export interface SkeletonLoaderProps extends HTMLAttributes<HTMLDivElement> {
  /** Shape variant */
  variant: SkeletonVariant;
  /** Number of text lines (text variant only) */
  lines?: number;
  /** Custom width override */
  width?: string;
  /** Custom height override */
  height?: string;
}

export const SkeletonLoader = forwardRef<HTMLDivElement, SkeletonLoaderProps>(
  ({ variant, lines = 3, width, height, className, style, ...rest }, ref) => {
    const cls = [styles.skeleton, className].filter(Boolean).join(' ');

    const mergedStyle = { ...style, ...(width ? { width } : {}), ...(height ? { height } : {}) };

    if (variant === 'text') {
      return (
        <div
          ref={ref}
          className={cls}
          role="status"
          aria-label="Loading content"
          aria-busy="true"
          style={mergedStyle}
          {...rest}
        >
          <span className={styles.srOnly}>Loading...</span>
          {Array.from({ length: lines }, (_, i) => (
            <div
              key={i}
              className={styles.textLine}
              style={{
                width: i === lines - 1 ? '60%' : '100%',
              }}
              aria-hidden="true"
            />
          ))}
        </div>
      );
    }

    if (variant === 'card') {
      return (
        <div
          ref={ref}
          className={[cls, styles.cardSkeleton].join(' ')}
          role="status"
          aria-label="Loading card"
          aria-busy="true"
          style={mergedStyle}
          {...rest}
        >
          <span className={styles.srOnly}>Loading...</span>
          <div className={styles.cardImage} aria-hidden="true" />
          <div className={styles.cardBody} aria-hidden="true">
            <div className={styles.textLine} style={{ width: '70%' }} />
            <div className={styles.textLine} style={{ width: '50%' }} />
            <div className={styles.textLine} style={{ width: '85%' }} />
          </div>
        </div>
      );
    }

    if (variant === 'chart') {
      return (
        <div
          ref={ref}
          className={[cls, styles.chartSkeleton].join(' ')}
          role="status"
          aria-label="Loading chart"
          aria-busy="true"
          style={mergedStyle}
          {...rest}
        >
          <span className={styles.srOnly}>Loading...</span>
          <div className={styles.chartArea} aria-hidden="true">
            {Array.from({ length: 5 }, (_, i) => (
              <div
                key={i}
                className={styles.chartBar}
                style={{ height: `${30 + Math.random() * 50}%` }}
              />
            ))}
          </div>
        </div>
      );
    }

    /* table variant */
    return (
      <div
        ref={ref}
        className={[cls, styles.tableSkeleton].join(' ')}
        role="status"
        aria-label="Loading table"
        aria-busy="true"
        style={mergedStyle}
        {...rest}
      >
        <span className={styles.srOnly}>Loading...</span>
        <div className={styles.tableHeader} aria-hidden="true">
          {Array.from({ length: 4 }, (_, i) => (
            <div key={i} className={styles.tableCell} />
          ))}
        </div>
        {Array.from({ length: lines }, (_, i) => (
          <div key={i} className={styles.tableRow} aria-hidden="true">
            {Array.from({ length: 4 }, (_, j) => (
              <div key={j} className={styles.tableCell} />
            ))}
          </div>
        ))}
      </div>
    );
  },
);

SkeletonLoader.displayName = 'SkeletonLoader';

export default SkeletonLoader;
