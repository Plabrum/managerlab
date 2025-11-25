'use client';

import { Pie, PieChart, Cell, ResponsiveContainer } from 'recharts';
import { cn } from '@/lib/utils';

const previewData = [
  { name: 'A', value: 35 },
  { name: 'B', value: 25 },
  { name: 'C', value: 20 },
  { name: 'D', value: 20 },
];

const COLORS = [
  'hsl(var(--chart-1))',
  'hsl(var(--chart-2))',
  'hsl(var(--chart-3))',
  'hsl(var(--chart-4))',
];

interface PieChartPreviewProps {
  className?: string;
}

export function PieChartPreview({ className }: PieChartPreviewProps) {
  return (
    <div className={cn('h-12 w-full', className)}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={previewData}
            dataKey="value"
            cx="50%"
            cy="50%"
            outerRadius="90%"
            innerRadius="0%"
          >
            {previewData.map((entry, index) => (
              <Cell
                key={`cell-${entry.name}`}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
