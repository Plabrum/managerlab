import type { ComponentType } from 'react';
import type { LucideIcon } from 'lucide-react';
import type { WidgetQuery, WidgetSize, WidgetType } from '@/types/dashboard';
import type { TimeSeriesDataResponse } from '@/openapi/ariveAPI.schemas';

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
  query: WidgetQuery;
}

export interface WidgetSizeConstraints {
  minW: number;
  minH: number;
  maxW?: number;
  maxH?: number;
  defaultW: number;
  defaultH: number;
}

export interface WidgetRegistryEntry {
  metadata: WidgetMetadata;
  defaults: WidgetDefaultConfig;
  sizeConstraints: WidgetSizeConstraints;
  // Widget components are now pure presentational - they receive data as props
  component: ComponentType<{ data: TimeSeriesDataResponse }>;
  preview: ComponentType<{ className?: string }>;
}

export type WidgetRegistry = Record<WidgetType, WidgetRegistryEntry>;
