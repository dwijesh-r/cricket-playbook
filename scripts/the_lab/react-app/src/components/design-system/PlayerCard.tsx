import { forwardRef, type HTMLAttributes } from 'react';
import styles from './PlayerCard.module.css';

export interface PlayerStat {
  /** Metric label */
  label: string;
  /** Metric value */
  value: string | number;
}

export interface PlayerCardProps extends Omit<HTMLAttributes<HTMLDivElement>, 'onClick'> {
  /** Player name */
  name: string;
  /** Team name */
  team: string;
  /** Player role (e.g., Batter, Bowler, All-rounder) */
  role: string;
  /** Player headshot URL */
  imageUrl?: string;
  /** Key performance stats (up to 3 recommended) */
  stats?: PlayerStat[];
  /** Click handler */
  onClick?: () => void;
}

export const PlayerCard = forwardRef<HTMLDivElement, PlayerCardProps>(
  ({ name, team, role, imageUrl, stats, onClick, className, ...rest }, ref) => {
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
        aria-label={`${name}, ${team}, ${role}`}
        {...interactiveProps}
        {...rest}
      >
        {/* Headshot */}
        <div className={styles.imageWrapper}>
          {imageUrl ? (
            <img
              src={imageUrl}
              alt={`${name} headshot`}
              className={styles.image}
              loading="lazy"
            />
          ) : (
            <div className={styles.placeholder} aria-hidden="true">
              <svg
                className={styles.avatarSvg}
                viewBox="0 0 64 64"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
              >
                <circle cx="32" cy="24" r="12" fill="#C4C4C4" />
                <ellipse cx="32" cy="52" rx="20" ry="14" fill="#C4C4C4" />
              </svg>
            </div>
          )}
        </div>

        {/* Info */}
        <div className={styles.info}>
          <h3 className={styles.name}>{name}</h3>
          <p className={styles.team}>{team}</p>
          <span className={styles.roleBadge} role="status">
            {role}
          </span>
        </div>

        {/* Stats row */}
        {stats && stats.length > 0 && (
          <div className={styles.statsRow} aria-label="Player statistics">
            {stats.slice(0, 3).map((stat) => (
              <div key={stat.label} className={styles.stat}>
                <span className={styles.statValue}>{stat.value}</span>
                <span className={styles.statLabel}>{stat.label}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  },
);

PlayerCard.displayName = 'PlayerCard';

export default PlayerCard;
