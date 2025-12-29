import { Area, AreaChart, ResponsiveContainer } from 'recharts';
import { cn } from '@/lib/utils';

const previewData = [
  { value: 30 },
  { value: 45 },
  { value: 35 },
  { value: 60 },
  { value: 50 },
  { value: 75 },
  { value: 65 },
];

interface LineChartPreviewProps {
  className?: string;
}

export function LineChartPreview({ className }: LineChartPreviewProps) {
  return (
    <div className={cn('h-12 w-full', className)}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={previewData}>
          <defs>
            <linearGradient id="linePreviewFill" x1="0" y1="0" x2="0" y2="1">
              <stop
                offset="5%"
                stopColor="hsl(var(--chart-1))"
                stopOpacity={0.8}
              />
              <stop
                offset="95%"
                stopColor="hsl(var(--chart-1))"
                stopOpacity={0.1}
              />
            </linearGradient>
          </defs>
          <Area
            dataKey="value"
            type="natural"
            fill="url(#linePreviewFill)"
            stroke="hsl(var(--chart-1))"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
