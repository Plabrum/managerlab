'use client';

import { Bar, BarChart, ResponsiveContainer } from 'recharts';
import { cn } from '@/lib/utils';

const previewData = [
  { value: 40 },
  { value: 65 },
  { value: 45 },
  { value: 80 },
  { value: 55 },
  { value: 70 },
];

interface BarChartPreviewProps {
  className?: string;
}

export function BarChartPreview({ className }: BarChartPreviewProps) {
  return (
    <div className={cn('h-12 w-full', className)}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={previewData}>
          <Bar dataKey="value" fill="hsl(var(--chart-1))" radius={2} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
