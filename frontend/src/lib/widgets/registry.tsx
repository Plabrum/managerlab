import { BarChart2, LineChart, PieChart, Hash } from 'lucide-react';
import {
  StatWidget,
  BarChartWidget,
  LineChartWidget,
  PieChartWidget,
} from '@/components/dashboard/widgets';
import {
  StatPreview,
  BarChartPreview,
  LineChartPreview,
  PieChartPreview,
} from '@/components/dashboard/widgets/previews';
import type { WidgetRegistry, WidgetType, WidgetRegistryEntry } from './types';

export const widgetRegistry: WidgetRegistry = {
  bar_chart: {
    metadata: {
      type: 'bar_chart',
      name: 'Bar Chart',
      description: 'Display data as vertical bars',
      icon: BarChart2,
      category: 'chart',
    },
    defaults: {
      size: { w: 3, h: 2 },
      query: {
        object_type: 'brands' as const,
        field: 'created_at',
        time_range: 'last_30_days' as const,
        granularity: 'automatic' as const,
        aggregation: 'count_' as const,
        filters: [],
        fill_missing: true,
      },
    },
    sizeConstraints: {
      minW: 2,
      minH: 2,
      defaultW: 3,
      defaultH: 2,
    },
    component: BarChartWidget,
    preview: BarChartPreview,
  },
  line_chart: {
    metadata: {
      type: 'line_chart',
      name: 'Line Chart',
      description: 'Display trends over time',
      icon: LineChart,
      category: 'chart',
    },
    defaults: {
      size: { w: 3, h: 2 },
      query: {
        object_type: 'brands' as const,
        field: 'created_at',
        time_range: 'last_30_days' as const,
        granularity: 'automatic' as const,
        aggregation: 'count_' as const,
        filters: [],
        fill_missing: true,
      },
    },
    sizeConstraints: {
      minW: 2,
      minH: 2,
      defaultW: 3,
      defaultH: 2,
    },
    component: LineChartWidget,
    preview: LineChartPreview,
  },
  pie_chart: {
    metadata: {
      type: 'pie_chart',
      name: 'Pie Chart',
      description: 'Display data distribution',
      icon: PieChart,
      category: 'chart',
    },
    defaults: {
      size: { w: 2, h: 2 },
      query: {
        object_type: 'brands' as const,
        field: 'status',
        time_range: 'last_30_days' as const,
        filters: [],
        fill_missing: true,
      },
    },
    sizeConstraints: {
      minW: 2,
      minH: 2,
      defaultW: 2,
      defaultH: 2,
    },
    component: PieChartWidget,
    preview: PieChartPreview,
  },
  stat_number: {
    metadata: {
      type: 'stat_number',
      name: 'Stat Number',
      description: 'Display a single metric with trend',
      icon: Hash,
      category: 'stat',
    },
    defaults: {
      size: { w: 1, h: 1 },
      query: {
        object_type: 'brands' as const,
        field: 'created_at',
        time_range: 'last_30_days' as const,
        aggregation: 'count_' as const,
        granularity: 'automatic' as const,
        filters: [],
        fill_missing: true,
      },
    },
    sizeConstraints: {
      minW: 1,
      minH: 1,
      defaultW: 1,
      defaultH: 1,
    },
    component: StatWidget,
    preview: StatPreview,
  },
};

export function getWidgetEntry(type: WidgetType): WidgetRegistryEntry {
  return widgetRegistry[type];
}

export function getWidgetComponent(type: WidgetType) {
  return widgetRegistry[type].component;
}

export function getWidgetPreview(type: WidgetType) {
  return widgetRegistry[type].preview;
}

export function getAllWidgetTypes(): WidgetType[] {
  return Object.keys(widgetRegistry) as WidgetType[];
}

export function getWidgetsByCategory(category: string) {
  return Object.values(widgetRegistry).filter(
    (entry) => entry.metadata.category === category
  );
}

export function getWidgetSizeConstraints(type: WidgetType) {
  return widgetRegistry[type].sizeConstraints;
}
