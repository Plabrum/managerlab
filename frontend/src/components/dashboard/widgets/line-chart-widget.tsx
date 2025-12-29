import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from 'recharts';
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart';
import { getChartColor } from '@/lib/utils';
import type { TimeSeriesDataResponse } from '@/openapi/ariveAPI.schemas';

interface LineChartWidgetProps {
  data: TimeSeriesDataResponse;
}

/**
 * Pure presentational line chart widget.
 * Receives data as props - no data fetching logic.
 */
export function LineChartWidget({ data }: LineChartWidgetProps) {
  if (data.data.type !== 'numerical') {
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
  );
}
