'use client';

import { useState, useEffect } from 'react';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { QueryBuilderForm } from './query-builder-form';
import type { WidgetConfig, WidgetType, WidgetQuery } from '@/types/dashboard';

interface WidgetEditorDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  widget: WidgetConfig | null;
  onSave: (widget: WidgetConfig) => void;
}

const WIDGET_TYPES: Array<{ value: WidgetType; label: string }> = [
  { value: 'bar_chart', label: 'Bar Chart' },
  { value: 'line_chart', label: 'Line Chart' },
  { value: 'pie_chart', label: 'Pie Chart' },
  { value: 'stat_number', label: 'Stat Number' },
];

export function WidgetEditorDrawer({
  open,
  onOpenChange,
  widget,
  onSave,
}: WidgetEditorDrawerProps) {
  const [widgetType, setWidgetType] = useState<WidgetType>('bar_chart');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [query, setQuery] = useState<WidgetQuery>({
    object_type: 'brands',
    field: 'created_at',
    time_range: 'last_30_days',
    granularity: 'automatic',
  });

  // Reset form when widget changes
  useEffect(() => {
    if (widget) {
      setWidgetType(widget.type);
      setTitle(widget.display.title);
      setDescription(widget.display.description || '');
      setQuery(widget.query);
    } else {
      // Reset to defaults for new widget
      setWidgetType('bar_chart');
      setTitle('');
      setDescription('');
      setQuery({
        object_type: 'brands',
        field: 'created_at',
        time_range: 'last_30_days',
        granularity: 'automatic',
      });
    }
  }, [widget, open]);

  const handleSave = () => {
    const newWidget: WidgetConfig = {
      id: widget?.id || `widget-${Date.now()}`,
      type: widgetType,
      position: widget?.position || { x: 0, y: 0 },
      size: widget?.size || { w: 1, h: 1 },
      query,
      display: {
        title,
        description: description || undefined,
      },
    };

    onSave(newWidget);
    onOpenChange(false);
  };

  const isValid = title.trim() !== '' && query.field !== '';

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full overflow-y-auto p-0 sm:max-w-lg">
        <div className="p-6">
          <SheetHeader>
            <SheetTitle>{widget ? 'Edit Widget' : 'Add Widget'}</SheetTitle>
            <SheetDescription>Configure your dashboard widget</SheetDescription>
          </SheetHeader>

          <div className="space-y-6 py-6">
            {/* Widget Type */}
            <div className="space-y-2">
              <Label htmlFor="widget-type">Widget Type</Label>
              <Select
                value={widgetType}
                onValueChange={(value) => setWidgetType(value as WidgetType)}
              >
                <SelectTrigger id="widget-type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {WIDGET_TYPES.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Title */}
            <div className="space-y-2">
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Widget title"
              />
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Description (optional)</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Widget description"
                rows={2}
              />
            </div>

            {/* Query Configuration */}
            <div className="space-y-2">
              <Label>Data Query</Label>
              <div className="rounded-lg border p-4">
                <QueryBuilderForm query={query} onChange={setQuery} />
              </div>
            </div>
          </div>

          <div className="border-t">
            <SheetFooter className="p-6">
              <Button variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={!isValid}>
                {widget ? 'Update' : 'Add'} Widget
              </Button>
            </SheetFooter>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}
