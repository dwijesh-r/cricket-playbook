import { forwardRef, type HTMLAttributes, type ReactNode } from 'react';
import styles from './Badge.module.css';

export type BadgeVariant = 'active' | 'coming-soon' | 'success' | 'warning' | 'error';
export type BadgeSize = 'sm' | 'md';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  /** Color variant */
  variant: BadgeVariant;
  /** Size preset */
  size?: BadgeSize;
  children: ReactNode;
}

const variantMap: Record<BadgeVariant, string> = {
  active: styles.active,
  'coming-soon': styles.comingSoon,
  success: styles.success,
  warning: styles.warning,
  error: styles.error,
};

const sizeMap: Record<BadgeSize, string> = {
  sm: styles.sm,
  md: styles.md,
};

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ variant, size = 'md', className, children, ...rest }, ref) => {
    const cls = [styles.badge, variantMap[variant], sizeMap[size], className]
      .filter(Boolean)
      .join(' ');

    return (
      <span ref={ref} className={cls} role="status" {...rest}>
        {children}
      </span>
    );
  },
);

Badge.displayName = 'Badge';

export default Badge;
