'use client';

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PencilIcon } from 'lucide-react';
import type { WidgetConfig } from '@/types/dashboard';

interface WidgetContainerProps {
  widget: WidgetConfig;
  onEdit: (widget: WidgetConfig) => void;
  children: React.ReactNode;
}

export function WidgetContainer({
  widget,
  onEdit,
  children,
}: WidgetContainerProps) {
  return (
    <Card className="flex h-full flex-col gap-y-0 px-4 py-6">
      <CardHeader className="flex flex-row items-start justify-between space-y-0 p-0">
        <div className="space-y-0">
          <CardTitle className="text-base font-medium">
            {widget.display.title}
          </CardTitle>
          {widget.display.description && (
            <CardDescription className="text-sm">
              {widget.display.description}
            </CardDescription>
          )}
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onEdit(widget)}
          className="h-8 w-8 p-0"
        >
          <PencilIcon className="h-4 w-4" />
          <span className="sr-only">Edit widget</span>
        </Button>
      </CardHeader>
      <CardContent className="flex-1 px-0">{children}</CardContent>
    </Card>
  );
}
