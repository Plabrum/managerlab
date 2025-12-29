import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from 'recharts';
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
} from '@/components/ui/chart';
import { getChartColor } from '@/lib/utils';
import type { TimeSeriesDataResponse } from '@/openapi/ariveAPI.schemas';
import type { TooltipProps } from 'recharts';

interface BarChartWidgetProps {
  data: TimeSeriesDataResponse;
}

/**
 * Custom tooltip that filters out zero values
 */
function FilteredTooltipContent(props: TooltipProps<number, string>) {
  const { payload, active, label } = props;

  // Filter out items with zero or null values
  const filteredPayload = payload?.filter((item) => {
    const value = item.value;
    return value !== null && value !== undefined && value !== 0;
  });

  return (
    <ChartTooltipContent
      active={active}
      payload={filteredPayload}
      label={label}
      className="min-w-[12rem]"
    />
  );
}

/**
 * Pure presentational bar chart widget.
 * Receives data as props - no data fetching logic.
 */
export function BarChartWidget({ data }: BarChartWidgetProps) {
  // Determine date formatting based on granularity
  const getDateFormat = (granularity: string | undefined) => {
    switch (granularity) {
      case 'day':
        return { month: 'short', day: 'numeric' } as const;
      case 'week':
        return { month: 'short', day: 'numeric' } as const;
      case 'month':
        return { month: 'short', year: 'numeric' } as const;
      case 'quarter':
        return { month: 'short', year: 'numeric' } as const;
      case 'year':
        return { year: 'numeric' } as const;
      default:
        return { month: 'short', day: 'numeric' } as const;
    }
  };

  // Handle numerical data (simple time series)
  if (data.data.type === 'numerical') {
    const dateFormat = getDateFormat(data.granularity_used);

    const chartData = data.data.data_points.map((point) => ({
      timestamp: new Date(point.timestamp).toLocaleDateString(
        'en-US',
        dateFormat
      ),
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
        <BarChart data={chartData}>
          <CartesianGrid vertical={false} />
          <XAxis
            dataKey="timestamp"
            tickLine={false}
            tickMargin={10}
            axisLine={false}
          />
          <YAxis tickLine={false} tickMargin={10} axisLine={false} />
          <ChartTooltip content={<ChartTooltipContent />} />
          <Bar dataKey="value" fill="var(--color-value)" radius={4} />
        </BarChart>
      </ChartContainer>
    );
  }

  // Handle categorical data (breakdowns over time)
  if (data.data.type === 'categorical') {
    // Calculate total count for each category across all time periods
    const categoryTotals: Record<string, number> = {};
    data.data.data_points.forEach((point) => {
      Object.entries(point.breakdowns).forEach(([category, count]) => {
        categoryTotals[category] = (categoryTotals[category] || 0) + count;
      });
    });

    // Sort categories by total and take top 8, group rest as "Others"
    const MAX_CATEGORIES = 8;
    const sortedCategories = Object.entries(categoryTotals)
      .sort(([, a], [, b]) => b - a)
      .map(([category]) => category);

    const topCategories = sortedCategories.slice(0, MAX_CATEGORIES);
    const hasOthers = sortedCategories.length > MAX_CATEGORIES;

    // Create a mapping of sanitized keys to original category names
    const categoryKeyMap = new Map<string, string>();
    topCategories.forEach((category) => {
      const sanitizedKey = `cat_${category.replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_]/g, '')}`;
      categoryKeyMap.set(sanitizedKey, category);
    });

    if (hasOthers) {
      categoryKeyMap.set('cat_Others', 'Others');
    }

    const dateFormat = getDateFormat(data.granularity_used);

    // Transform data for stacked bar chart
    const chartData = data.data.data_points.map((point) => {
      const row: Record<string, string | number> = {
        timestamp: new Date(point.timestamp).toLocaleDateString(
          'en-US',
          dateFormat
        ),
      };

      // Add top categories
      topCategories.forEach((category) => {
        const sanitizedKey = `cat_${category.replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_]/g, '')}`;
        row[sanitizedKey] = point.breakdowns[category] || 0;
      });

      // Add "Others" category if needed
      if (hasOthers) {
        const othersTotal = Object.entries(point.breakdowns)
          .filter(([category]) => !topCategories.includes(category))
          .reduce((sum, [, count]) => sum + count, 0);
        row['cat_Others'] = othersTotal;
      }

      return row;
    });

    // Create chart config for each category using sanitized keys
    const chartConfig: ChartConfig = {};
    let colorIndex = 0;
    categoryKeyMap.forEach((originalCategory, sanitizedKey) => {
      chartConfig[sanitizedKey] = {
        label: originalCategory,
        color: getChartColor(colorIndex++),
      };
    });

    if (chartData.length === 0 || categoryKeyMap.size === 0) {
      return (
        <div className="flex h-full items-center justify-center">
          <div className="text-muted-foreground text-sm">No data available</div>
        </div>
      );
    }

    // Only show legend if we have 6 or fewer categories
    const showLegend = categoryKeyMap.size <= 6;

    return (
      <ChartContainer config={chartConfig} className="h-full w-full">
        <BarChart data={chartData}>
          <CartesianGrid vertical={false} />
          <XAxis
            dataKey="timestamp"
            tickLine={false}
            tickMargin={10}
            axisLine={false}
          />
          <YAxis tickLine={false} tickMargin={10} axisLine={false} />
          <ChartTooltip content={<FilteredTooltipContent />} />
          {showLegend && <ChartLegend content={<ChartLegendContent />} />}
          {Array.from(categoryKeyMap.keys()).map((sanitizedKey) => (
            <Bar
              key={sanitizedKey}
              dataKey={sanitizedKey}
              stackId="a"
              fill={`var(--color-${sanitizedKey})`}
              radius={[4, 4, 0, 0]}
            />
          ))}
        </BarChart>
      </ChartContainer>
    );
  }

  // Unsupported data type
  return (
    <div className="flex h-full items-center justify-center">
      <div className="text-muted-foreground text-sm">No data available</div>
    </div>
  );
}
