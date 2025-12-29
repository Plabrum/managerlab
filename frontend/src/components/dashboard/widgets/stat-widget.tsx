import { ArrowUpIcon, ArrowDownIcon, MinusIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { TimeSeriesDataResponse } from '@/openapi/ariveAPI.schemas';

interface StatWidgetProps {
  data: TimeSeriesDataResponse;
}

/**
 * Pure presentational stat widget.
 * Receives data as props - no data fetching logic.
 */
export function StatWidget({ data }: StatWidgetProps) {
  if (data.data.type !== 'numerical') {
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
            {trend === 'up' ? '+' : ''}
            {Math.abs(trendPercentage).toFixed(1)}%
          </span>
        </div>
      )}
    </div>
  );
}
