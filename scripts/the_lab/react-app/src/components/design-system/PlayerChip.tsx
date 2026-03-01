import { forwardRef, type HTMLAttributes } from 'react';
import styles from './PlayerChip.module.css';
import { colors } from '../../theme/tokens';

export type PlayerRole = 'batter' | 'bowler' | 'all-rounder' | 'keeper';

export interface PlayerChipProps extends HTMLAttributes<HTMLSpanElement> {
  /** Player display name */
  name: string;
  /** Team abbreviation (CSK, MI, RCB, etc.) — determines dot color */
  team: string;
  /** Player role — determines icon */
  role: PlayerRole;
  /** Optional click handler (makes chip interactive) */
  onClick?: () => void;
}

const roleIcons: Record<PlayerRole, string> = {
  batter: '\uD83C\uDFCF', // cricket bat emoji
  bowler: '\u26BE', // baseball (closest to ball)
  'all-rounder': '\u2726', // four-pointed star
  keeper: '\uD83E\uDDE4', // gloves emoji
};

const roleLabels: Record<PlayerRole, string> = {
  batter: 'Batter',
  bowler: 'Bowler',
  'all-rounder': 'All-rounder',
  keeper: 'Wicketkeeper',
};

export const PlayerChip = forwardRef<HTMLSpanElement, PlayerChipProps>(
  ({ name, team, role, onClick, className, ...rest }, ref) => {
    const teamColor =
      colors.team[team as keyof typeof colors.team] ?? 'var(--text-tertiary)';

    const isClickable = !!onClick;

    const cls = [styles.chip, isClickable ? styles.clickable : '', className]
      .filter(Boolean)
      .join(' ');

    const chipProps: HTMLAttributes<HTMLSpanElement> & {
      tabIndex?: number;
      role?: string;
    } = {};

    if (isClickable) {
      chipProps.role = 'button';
      chipProps.tabIndex = 0;
      chipProps.onKeyDown = (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      };
    }

    return (
      <span
        ref={ref}
        className={cls}
        onClick={onClick}
        aria-label={`${name}, ${team}, ${roleLabels[role]}`}
        {...chipProps}
        {...rest}
      >
        <span
          className={styles.dot}
          style={{ backgroundColor: teamColor }}
          aria-hidden="true"
        />
        <span className={styles.name}>{name}</span>
        <span className={styles.role} aria-hidden="true" title={roleLabels[role]}>
          {roleIcons[role]}
        </span>
      </span>
    );
  },
);

PlayerChip.displayName = 'PlayerChip';

export default PlayerChip;
