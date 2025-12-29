import { Card, CardContent } from '@/components/ui/card';
import type React from 'react';

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

export function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <Card className="border-0 bg-gray-900 shadow-lg transition-shadow duration-300 hover:shadow-xl">
      <CardContent className="space-y-4 p-8">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gray-700 text-gray-300">
          {icon}
        </div>
        <h3 className="text-xl font-bold text-white">{title}</h3>
        <p className="leading-relaxed text-gray-400">{description}</p>
      </CardContent>
    </Card>
  );
}
