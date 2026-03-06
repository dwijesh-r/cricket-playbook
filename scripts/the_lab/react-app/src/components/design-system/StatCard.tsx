import { forwardRef, type HTMLAttributes } from 'react';
import styles from './StatCard.module.css';

export type StatCardTrend = 'up' | 'down' | 'neutral';

export interface StatCardProps extends Omit<HTMLAttributes<HTMLDivElement>, 'title'> {
  /** KPI label displayed above the metric */
  title: string;
  /** Primary metric value */
  value: string | number;
  /** Comparison text (e.g., "+12% vs league average") */
  comparison: string;
  /** Trend direction — determines color and arrow indicator */
  trend: StatCardTrend;
}

const trendColorMap: Record<StatCardTrend, string> = {
  up: styles.trendUp,
  down: styles.trendDown,
  neutral: styles.trendNeutral,
};

const accentBarMap: Record<StatCardTrend, string> = {
  up: styles.accentBarUp,
  down: styles.accentBarDown,
  neutral: styles.accentBarNeutral,
};

const trendArrowMap: Record<StatCardTrend, string> = {
  up: '\u2191',    // arrow up
  down: '\u2193',  // arrow down
  neutral: '\u2192', // arrow right
};

const trendLabelMap: Record<StatCardTrend, string> = {
  up: 'Trending up',
  down: 'Trending down',
  neutral: 'No change',
};

export const StatCard = forwardRef<HTMLDivElement, StatCardProps>(
  ({ title, value, comparison, trend, className, ...rest }, ref) => {
    const cls = [styles.statCard, className].filter(Boolean).join(' ');
    const trendCls = trendColorMap[trend];

    return (
      <div
        ref={ref}
        className={cls}
        role="figure"
        aria-label={`${title}: ${value}. ${comparison}. ${trendLabelMap[trend]}.`}
        {...rest}
      >
        {/* Left accent bar */}
        <span
          className={`${styles.accentBar} ${accentBarMap[trend]}`}
          aria-hidden="true"
        />

        {/* Title label */}
        <p className={styles.title}>{title}</p>

        {/* Large metric */}
        <p className={styles.value}>{value}</p>

        {/* Comparison indicator */}
        <p className={`${styles.comparison} ${trendCls}`}>
          <span className={styles.trendIcon} aria-hidden="true">
            {trendArrowMap[trend]}
          </span>
          {comparison}
        </p>
      </div>
    );
  },
);

StatCard.displayName = 'StatCard';

export default StatCard;
