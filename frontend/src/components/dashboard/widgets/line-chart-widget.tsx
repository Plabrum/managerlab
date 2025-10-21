'use client';

import { useEffect, useState } from 'react';
import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from 'recharts';
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

interface LineChartWidgetProps {
  query: WidgetQuery;
}

export function LineChartWidget({ query }: LineChartWidgetProps) {
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
          fill_missing: true,
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

  if (!data || data.data.type !== 'numerical') {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-muted-foreground text-sm">No data available</div>
      </div>
    );
  }

  // Transform data for recharts
  const chartData = data.data.data_points.map((point) => ({
    timestamp: new Date(point.timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    }),
    value: point.value ?? 0,
  }));

  const chartConfig = {
    value: {
      label: data.field_name,
      color: getChartColor(0),
    },
  } satisfies ChartConfig;

  return (
    <div className="h-full w-full">
      <ChartContainer config={chartConfig} className="h-full w-full">
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="fillValue" x1="0" y1="0" x2="0" y2="1">
              <stop
                offset="5%"
                stopColor="var(--color-value)"
                stopOpacity={0.8}
              />
              <stop
                offset="95%"
                stopColor="var(--color-value)"
                stopOpacity={0.1}
              />
            </linearGradient>
          </defs>
          <CartesianGrid vertical={false} />
          <XAxis
            dataKey="timestamp"
            tickLine={false}
            tickMargin={10}
            axisLine={false}
          />
          <YAxis tickLine={false} tickMargin={10} axisLine={false} />
          <ChartTooltip content={<ChartTooltipContent />} />
          <Area
            dataKey="value"
            type="natural"
            fill="url(#fillValue)"
            stroke="var(--color-value)"
          />
        </AreaChart>
      </ChartContainer>
    </div>
  );
}
