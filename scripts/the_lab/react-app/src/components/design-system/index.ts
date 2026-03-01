/**
 * Design System — Barrel Export
 *
 * Re-exports all design system components and their types
 * for convenient single-import usage:
 *
 *   import { Card, Badge, Table, Tabs, Modal, PlayerChip } from '@components/design-system';
 */

export { Card, default as CardDefault } from './Card';
export type { CardProps, CardVariant, CardPadding } from './Card';

export { Badge, default as BadgeDefault } from './Badge';
export type { BadgeProps, BadgeVariant, BadgeSize } from './Badge';

export { Table, default as TableDefault } from './Table';
export type { TableProps, TableColumn, SortDirection } from './Table';

export { Tabs, TabPanel, default as TabsDefault } from './Tabs';
export type { TabsProps, TabItem, TabPanelProps } from './Tabs';

export { Modal, default as ModalDefault } from './Modal';
export type { ModalProps, ModalSize } from './Modal';

export { PlayerChip, default as PlayerChipDefault } from './PlayerChip';
export type { PlayerChipProps, PlayerRole } from './PlayerChip';
