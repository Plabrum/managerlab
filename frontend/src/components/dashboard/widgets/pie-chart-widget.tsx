'use client';

import { Pie, PieChart, Cell } from 'recharts';
import type { TimeSeriesDataResponse } from '@/openapi/ariveAPI.schemas';
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
} from '@/components/ui/chart';
import { getChartColor } from '@/lib/utils';

interface PieChartWidgetProps {
  data: TimeSeriesDataResponse;
}

/**
 * Pure presentational pie chart widget.
 * Receives data as props - no data fetching logic.
 */
export function PieChartWidget({ data }: PieChartWidgetProps) {
  if (data.data.type !== 'categorical') {
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

  console.log('PieChartWidget - chartData:', chartData);
  if (chartData.length === 0) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-muted-foreground text-sm">No data available</div>
      </div>
    );
  }

  return (
    <ChartContainer config={chartConfig} className="h-full w-full">
      <PieChart>
        <ChartTooltip content={<ChartTooltipContent />} />
        <Pie
          data={chartData}
          dataKey="value"
          nameKey="name"
          cx="40%"
          cy="50%"
          outerRadius="70%"
          innerRadius="40%"
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${entry.name}`} fill={getChartColor(index)} />
          ))}
        </Pie>
        <ChartLegend
          layout="vertical"
          verticalAlign="middle"
          align="right"
          content={
            <ChartLegendContent
              nameKey="name"
              className="flex flex-col gap-2"
            />
          }
        />
      </PieChart>
    </ChartContainer>
  );
}
