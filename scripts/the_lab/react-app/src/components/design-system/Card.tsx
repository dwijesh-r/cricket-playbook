import { forwardRef, type HTMLAttributes, type ReactNode } from 'react';
import styles from './Card.module.css';

export type CardVariant = 'default' | 'elevated' | 'outlined';
export type CardPadding = 'none' | 'sm' | 'md' | 'lg';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  /** Visual style variant */
  variant?: CardVariant;
  /** Padding preset */
  padding?: CardPadding;
  children: ReactNode;
}

const paddingMap: Record<CardPadding, string> = {
  none: styles.padNone,
  sm: styles.padSm,
  md: styles.padMd,
  lg: styles.padLg,
};

const variantMap: Record<CardVariant, string> = {
  default: '',
  elevated: styles.elevated,
  outlined: styles.outlined,
};

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ variant = 'default', padding = 'md', className, children, ...rest }, ref) => {
    const cls = [
      styles.card,
      variantMap[variant],
      paddingMap[padding],
      className,
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <div ref={ref} className={cls} {...rest}>
        {children}
      </div>
    );
  },
);

Card.displayName = 'Card';

export default Card;
