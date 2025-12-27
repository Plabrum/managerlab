'use client';

import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Star } from 'lucide-react';
import type { SavedViewSchema } from '@/openapi/ariveAPI.schemas';

interface SavedViewTabsProps {
  views: SavedViewSchema[];
  currentViewId: unknown | null | undefined;
  onViewSelect: (viewId: unknown) => void;
}

export function SavedViewTabs({
  views,
  currentViewId,
  onViewSelect,
}: SavedViewTabsProps) {
  // Only hide tabs when there are no saved views (only "Default" tab would show)
  if (views.length === 0) {
    return null;
  }

  // Use 'default' as the value for hard-coded default view
  const tabValue =
    currentViewId === null || currentViewId === undefined
      ? 'default'
      : String(currentViewId);

  return (
    <Tabs
      value={tabValue}
      onValueChange={(value) => {
        if (value === 'default') {
          onViewSelect(null);
        } else {
          const view = views.find((v) => String(v.id) === value);
          if (view) onViewSelect(view.id);
        }
      }}
    >
      <TabsList>
        {/* Default tab - always show when there are saved views or when actively selected */}
        {(views.length > 0 || currentViewId === null) && (
          <TabsTrigger value="default" className="gap-1.5">
            Default
          </TabsTrigger>
        )}

        {/* Saved view tabs */}
        {views.map((view) => (
          <TabsTrigger
            key={String(view.id)}
            value={String(view.id)}
            className="gap-1.5"
          >
            {view.is_default && (
              <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
            )}
            {view.name}
          </TabsTrigger>
        ))}
      </TabsList>
    </Tabs>
  );
}
