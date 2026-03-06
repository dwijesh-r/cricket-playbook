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

export { StatCard, default as StatCardDefault } from './StatCard';
export type { StatCardProps, StatCardTrend } from './StatCard';

export { ChartContainer, default as ChartContainerDefault } from './ChartContainer';
export type { ChartContainerProps } from './ChartContainer';

export { DataVizColors, default as DataVizColorsDefault } from './DataVizColors';
export type { DataVizColorsType } from './DataVizColors';

export { MatchCard, default as MatchCardDefault } from './MatchCard';
export type { MatchCardProps, MatchStatus } from './MatchCard';

export { PlayerCard, default as PlayerCardDefault } from './PlayerCard';
export type { PlayerCardProps, PlayerStat } from './PlayerCard';

export { TeamCard, default as TeamCardDefault } from './TeamCard';
export type { TeamCardProps, FormResult } from './TeamCard';

export { FilterBar, default as FilterBarDefault } from './FilterBar';
export type { FilterBarProps, FilterDefinition } from './FilterBar';

export { NavBar, default as NavBarDefault } from './NavBar';
export type { NavBarProps, NavItem } from './NavBar';

export { Footer, default as FooterDefault } from './Footer';
export type { FooterProps, FooterSection } from './Footer';

export { SkeletonLoader, default as SkeletonLoaderDefault } from './SkeletonLoader';
export type { SkeletonLoaderProps, SkeletonVariant } from './SkeletonLoader';

export { InsightsPanel, default as InsightsPanelDefault } from './InsightsPanel';
export type { InsightsPanelProps, Insight, InsightType } from './InsightsPanel';
