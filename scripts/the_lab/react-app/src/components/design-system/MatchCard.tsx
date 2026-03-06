import { forwardRef, type HTMLAttributes } from 'react';
import styles from './MatchCard.module.css';

export type MatchStatus = 'upcoming' | 'live' | 'completed';

export interface MatchCardProps extends Omit<HTMLAttributes<HTMLDivElement>, 'onClick'> {
  /** First team name */
  teamA: string;
  /** Second team name */
  teamB: string;
  /** League name */
  league?: string;
  /** Match date display string */
  date?: string;
  /** Win probability for team A (0–100) */
  winProbA?: number;
  /** Win probability for team B (0–100) */
  winProbB?: number;
  /** Featured key player */
  keyPlayer?: string;
  /** Match status */
  status?: MatchStatus;
  /** Click handler */
  onClick?: () => void;
}

const statusLabels: Record<MatchStatus, string> = {
  upcoming: 'Upcoming',
  live: 'Live',
  completed: 'Completed',
};

export const MatchCard = forwardRef<HTMLDivElement, MatchCardProps>(
  (
    {
      teamA,
      teamB,
      league,
      date,
      winProbA,
      winProbB,
      keyPlayer,
      status = 'upcoming',
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

    const probA = winProbA ?? 50;
    const probB = winProbB ?? 50;

    return (
      <div
        ref={ref}
        className={cls}
        onClick={onClick}
        aria-label={`${teamA} vs ${teamB}${league ? `, ${league}` : ''}${date ? `, ${date}` : ''}, ${statusLabels[status]}`}
        {...interactiveProps}
        {...rest}
      >
        {/* Status indicator */}
        <div className={styles.statusRow}>
          <span
            className={[styles.statusBadge, styles[status]].join(' ')}
            role="status"
            aria-label={statusLabels[status]}
          >
            {status === 'live' && (
              <span className={styles.pulse} aria-hidden="true" />
            )}
            {statusLabels[status]}
          </span>
        </div>

        {/* Teams */}
        <div className={styles.teams}>
          <span className={styles.teamName}>{teamA}</span>
          <span className={styles.vs} aria-hidden="true">
            vs
          </span>
          <span className={styles.teamName}>{teamB}</span>
        </div>

        {/* League and date */}
        {(league || date) && (
          <div className={styles.meta}>
            {league && <span className={styles.league}>{league}</span>}
            {league && date && (
              <span className={styles.separator} aria-hidden="true">
                &middot;
              </span>
            )}
            {date && <time className={styles.date}>{date}</time>}
          </div>
        )}

        {/* Win probability bar */}
        {(winProbA != null || winProbB != null) && (
          <div
            className={styles.probBar}
            role="meter"
            aria-label={`Win probability: ${teamA} ${probA}%, ${teamB} ${probB}%`}
            aria-valuenow={probA}
            aria-valuemin={0}
            aria-valuemax={100}
          >
            <div className={styles.probLabels}>
              <span className={styles.probLabel}>{probA}%</span>
              <span className={styles.probLabel}>{probB}%</span>
            </div>
            <div className={styles.probTrack}>
              <div
                className={styles.probFillA}
                style={{ width: `${probA}%` }}
                aria-hidden="true"
              />
              <div
                className={styles.probFillB}
                style={{ width: `${probB}%` }}
                aria-hidden="true"
              />
            </div>
          </div>
        )}

        {/* Key player */}
        {keyPlayer && (
          <div className={styles.keyPlayer}>
            <span className={styles.keyPlayerLabel}>Key Player</span>
            <span className={styles.keyPlayerName}>{keyPlayer}</span>
          </div>
        )}
      </div>
    );
  },
);

MatchCard.displayName = 'MatchCard';

export default MatchCard;
