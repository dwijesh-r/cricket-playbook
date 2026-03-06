import { forwardRef, type HTMLAttributes } from 'react';
import styles from './TeamCard.module.css';

export type FormResult = 'W' | 'L' | 'NR';

export interface TeamCardProps extends Omit<HTMLAttributes<HTMLDivElement>, 'onClick'> {
  /** Team name */
  name: string;
  /** Team abbreviation (e.g., CSK, MI) */
  abbreviation: string;
  /** Team logo URL */
  logoUrl?: string;
  /** Current ranking */
  ranking?: number;
  /** Win rate (0–100) */
  winRate?: number;
  /** Recent form — array of 'W', 'L', or 'NR' */
  recentForm?: FormResult[];
  /** Click handler */
  onClick?: () => void;
}

const formColorMap: Record<FormResult, string> = {
  W: '#2ECC71',
  L: '#E74C3C',
  NR: '#A0A0A0',
};

const formLabelMap: Record<FormResult, string> = {
  W: 'Win',
  L: 'Loss',
  NR: 'No Result',
};

export const TeamCard = forwardRef<HTMLDivElement, TeamCardProps>(
  (
    {
      name,
      abbreviation,
      logoUrl,
      ranking,
      winRate,
      recentForm,
      onClick,
      className,
      ...rest
    },
    ref,
  ) => {
    const isClickable = !!onClick;

    const cls = [styles.card, isClickable ? styles.clickable : '', className]
      .filter(Boolean)
      .join(' ');

    const interactiveProps: HTMLAttributes<HTMLDivElement> & {
      tabIndex?: number;
      role?: string;
    } = {};

    if (isClickable) {
      interactiveProps.role = 'button';
      interactiveProps.tabIndex = 0;
      interactiveProps.onKeyDown = (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      };
    }

    return (
      <div
        ref={ref}
        className={cls}
        onClick={onClick}
        aria-label={`${name} (${abbreviation})${ranking != null ? `, Rank ${ranking}` : ''}${winRate != null ? `, ${winRate}% win rate` : ''}`}
        {...interactiveProps}
        {...rest}
      >
        {/* Logo / Abbreviation */}
        <div className={styles.logoArea}>
          {logoUrl ? (
            <img
              src={logoUrl}
              alt={`${name} logo`}
              className={styles.logo}
              loading="lazy"
            />
          ) : (
            <div className={styles.abbrCircle} aria-hidden="true">
              <span className={styles.abbrText}>{abbreviation}</span>
            </div>
          )}
        </div>

        {/* Name and ranking */}
        <div className={styles.info}>
          <h3 className={styles.name}>{name}</h3>
          {ranking != null && (
            <span className={styles.ranking}>
              Rank <strong>#{ranking}</strong>
            </span>
          )}
        </div>

        {/* Win rate */}
        {winRate != null && (
          <div className={styles.winRate}>
            <span className={styles.winRateValue}>{winRate}%</span>
            <span className={styles.winRateLabel}>Win Rate</span>
          </div>
        )}

        {/* Recent form */}
        {recentForm && recentForm.length > 0 && (
          <div
            className={styles.formRow}
            role="list"
            aria-label="Recent form"
          >
            {recentForm.map((result, idx) => (
              <span
                key={idx}
                className={styles.formDot}
                style={{ backgroundColor: formColorMap[result] }}
                role="listitem"
                aria-label={formLabelMap[result]}
                title={formLabelMap[result]}
              />
            ))}
          </div>
        )}
      </div>
    );
  },
);

TeamCard.displayName = 'TeamCard';

export default TeamCard;
