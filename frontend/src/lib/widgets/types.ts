import type { ComponentType } from 'react';
import type { LucideIcon } from 'lucide-react';
import type { WidgetQuery, WidgetSize, WidgetType } from '@/types/dashboard';

export type { WidgetType } from '@/types/dashboard';

export interface WidgetMetadata {
  type: WidgetType;
  name: string;
  description: string;
  icon: LucideIcon;
  category: 'chart' | 'stat' | 'table' | 'custom';
}

export interface WidgetDefaultConfig {
  size: WidgetSize;
  query: Partial<WidgetQuery>;
}

export interface WidgetRegistryEntry {
  metadata: WidgetMetadata;
  defaults: WidgetDefaultConfig;
  component: ComponentType<{ query: WidgetQuery }>;
  preview: ComponentType<{ className?: string }>;
}

export type WidgetRegistry = Record<WidgetType, WidgetRegistryEntry>;
