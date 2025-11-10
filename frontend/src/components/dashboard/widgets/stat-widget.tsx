'use client';

import { useEffect, useState } from 'react';
import { ArrowUpIcon, ArrowDownIcon, MinusIcon } from 'lucide-react';
import type { WidgetQuery } from '@/types/dashboard';
import { getTimeSeriesData } from '@/openapi/objects/objects';
import type { TimeSeriesDataResponse } from '@/openapi/ariveAPI.schemas';
import { cn } from '@/lib/utils';

interface StatWidgetProps {
  query: WidgetQuery;
}

export function StatWidget({ query }: StatWidgetProps) {
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

  // Calculate the current value (latest data point)
  const dataPoints = data.data.data_points;
  const latestPoint = dataPoints[dataPoints.length - 1];
  const currentValue = latestPoint?.value ?? 0;

  // Calculate trend (compare last two points)
  let trend: 'up' | 'down' | 'neutral' = 'neutral';
  let trendPercentage = 0;

  if (dataPoints.length >= 2) {
    const previousPoint = dataPoints[dataPoints.length - 2];
    const previousValue = previousPoint?.value ?? 0;

    if (previousValue !== 0) {
      trendPercentage =
        ((currentValue - previousValue) / Math.abs(previousValue)) * 100;
      trend =
        trendPercentage > 0 ? 'up' : trendPercentage < 0 ? 'down' : 'neutral';
    }
  }

  // Format value based on field type
  const formatValue = (value: number) => {
    if (data.field_type === 'usd') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(value);
    }

    if (data.field_type === 'float') {
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
      }).format(value);
    }

    return new Intl.NumberFormat('en-US').format(value);
  };

  const TrendIcon =
    trend === 'up' ? ArrowUpIcon : trend === 'down' ? ArrowDownIcon : MinusIcon;

  return (
    <div className="flex h-full flex-col items-center justify-center space-y-2">
      <div className="text-4xl font-bold">{formatValue(currentValue)}</div>

      {dataPoints.length >= 2 && (
        <div className="flex items-center gap-1">
          <TrendIcon
            className={cn(
              'h-4 w-4',
              trend === 'up' && 'text-green-500',
              trend === 'down' && 'text-red-500',
              trend === 'neutral' && 'text-gray-500'
            )}
          />
          <span
            className={cn(
              'text-sm font-medium',
              trend === 'up' && 'text-green-500',
              trend === 'down' && 'text-red-500',
              trend === 'neutral' && 'text-gray-500'
            )}
          >
            {Math.abs(trendPercentage).toFixed(1)}%
          </span>
          <span className="text-muted-foreground text-sm">
            vs previous period
          </span>
        </div>
      )}

      <div className="text-muted-foreground text-xs">
        Total records: {data.total_records}
      </div>
    </div>
  );
}
