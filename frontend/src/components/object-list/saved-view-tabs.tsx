import { Star } from 'lucide-react';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
  // Convert null/undefined to a string for tab value
  // System default has id=null, so we use 'null' as its string representation
  const tabValue =
    currentViewId === null || currentViewId === undefined
      ? 'null'
      : String(currentViewId);

  return (
    <Tabs
      value={tabValue}
      onValueChange={(value) => {
        if (value === 'null') {
          // System default view (id=null)
          onViewSelect(null);
        } else {
          // Find the view by ID
          const view = views.find((v) => String(v.id) === value);
          if (view) onViewSelect(view.id);
        }
      }}
    >
      <TabsList>
        {/* Render all views - backend decides which to include */}
        {views.map((view) => (
          <TabsTrigger
            key={String(view.id ?? 'null')}
            value={String(view.id ?? 'null')}
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
