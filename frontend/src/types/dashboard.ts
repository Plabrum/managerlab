import type {
  TimeSeriesDataRequestFiltersItem,
  TimeRange,
  Granularity,
  AggregationType,
  ObjectTypes,
} from '@/openapi/managerLab.schemas';

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

export interface WidgetQuery {
  object_type: ObjectTypes;
  field: string;
  time_range?: TimeRange;
  start_date?: string;
  end_date?: string;
  aggregation?: AggregationType;
  filters?: TimeSeriesDataRequestFiltersItem[];
  granularity?: Granularity;
}

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
