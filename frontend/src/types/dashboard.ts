import type { WidgetQuerySchema } from '@/openapi/ariveAPI.schemas';

export type WidgetType =
  | 'bar_chart'
  | 'line_chart'
  | 'pie_chart'
  | 'stat_number';

export interface WidgetPosition {
  x: number;
  y: number;
}

export interface WidgetSize {
  w: number;
  h: number;
}

// Use the generated type from backend
export type WidgetQuery = WidgetQuerySchema;

export interface WidgetDisplay {
  title: string;
  description?: string;
}

export interface WidgetConfig {
  id: string;
  type: WidgetType;
  position: WidgetPosition;
  size: WidgetSize;
  query: WidgetQuery;
  display: WidgetDisplay;
}

export interface DashboardConfig {
  widgets: WidgetConfig[];
}
