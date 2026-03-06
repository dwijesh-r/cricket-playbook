import { forwardRef, type HTMLAttributes } from 'react';
import styles from './InsightsPanel.module.css';

export type InsightType = 'positive' | 'negative' | 'neutral';

export interface Insight {
  /** Insight text */
  text: string;
  /** Sentiment / category */
  type?: InsightType;
}

export interface InsightsPanelProps extends HTMLAttributes<HTMLDivElement> {
  /** Panel heading */
  title?: string;
  /** List of analytical insights */
  insights: Insight[];
}

const typeColorMap: Record<InsightType, string> = {
  positive: '#2ECC71',
  negative: '#E74C3C',
  neutral: '#3498DB',
};

const typeLabelMap: Record<InsightType, string> = {
  positive: 'Positive trend',
  negative: 'Negative trend',
  neutral: 'Neutral observation',
};

export const InsightsPanel = forwardRef<HTMLDivElement, InsightsPanelProps>(
  ({ title, insights, className, ...rest }, ref) => {
    const cls = [styles.panel, className].filter(Boolean).join(' ');

    return (
      <div ref={ref} className={cls} role="region" aria-label={title ?? 'Insights'} {...rest}>
        {title && <h3 className={styles.title}>{title}</h3>}

        <ul className={styles.list}>
          {insights.map((insight, idx) => {
            const type = insight.type ?? 'neutral';
            return (
              <li key={idx} className={styles.item}>
                <span
                  className={styles.indicator}
                  style={{ backgroundColor: typeColorMap[type] }}
                  aria-label={typeLabelMap[type]}
                  role="img"
                />
                <span className={styles.text}>{insight.text}</span>
              </li>
            );
          })}
        </ul>
      </div>
    );
  },
);

InsightsPanel.displayName = 'InsightsPanel';

export default InsightsPanel;
