'use client';

import { useEffect, useState } from 'react';
import { Pie, PieChart, Cell, Legend } from 'recharts';
import type { WidgetQuery } from '@/types/dashboard';
import { getTimeSeriesData } from '@/openapi/objects/objects';
import type { TimeSeriesDataResponse } from '@/openapi/managerLab.schemas';
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart';
import { getChartColor } from '@/lib/utils';

interface PieChartWidgetProps {
  query: WidgetQuery;
}

export function PieChartWidget({ query }: PieChartWidgetProps) {
  const [data, setData] = useState<TimeSeriesDataResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await getTimeSeriesData(query.object_type, {
          field: query.field,
          time_range: query.time_range,
          start_date: query.start_date,
          end_date: query.end_date,
          aggregation: query.aggregation,
          filters: query.filters,
          granularity: query.granularity,
          fill_missing: false,
        });
        setData(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [query]);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-muted-foreground text-sm">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-destructive text-sm">{error}</div>
      </div>
    );
  }

  if (!data || data.data.type !== 'categorical') {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-muted-foreground text-sm">
          No categorical data available
        </div>
      </div>
    );
  }

  // Aggregate all categorical data across time periods
  const aggregatedData: Record<string, number> = {};

  data.data.data_points.forEach((point) => {
    Object.entries(point.breakdowns).forEach(([category, count]) => {
      aggregatedData[category] = (aggregatedData[category] || 0) + count;
    });
  });

  // Transform to chart format
  const chartData = Object.entries(aggregatedData).map(([name, value]) => ({
    name,
    value,
  }));

  // Create chart config
  const chartConfig: ChartConfig = {};
  Object.keys(aggregatedData).forEach((category, index) => {
    chartConfig[category] = {
      label: category,
      color: getChartColor(index),
    };
  });

  if (chartData.length === 0) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-muted-foreground text-sm">No data available</div>
      </div>
    );
  }

  return (
    <div className="h-full w-full">
      <ChartContainer config={chartConfig} className="h-full w-full">
        <PieChart>
          <ChartTooltip content={<ChartTooltipContent />} />
          <Pie
            data={chartData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={80}
            label
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getChartColor(index)} />
            ))}
          </Pie>
          <Legend />
        </PieChart>
      </ChartContainer>
    </div>
  );
}
