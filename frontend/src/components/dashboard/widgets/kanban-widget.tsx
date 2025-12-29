import { ObjectKanban } from '@/components/object-kanban';
import type {
  TimeSeriesDataResponse,
  ObjectTypes,
  WidgetQuerySchema,
} from '@/openapi/ariveAPI.schemas';

interface KanbanWidgetProps {
  data: TimeSeriesDataResponse; // Required by widget system but not used
  query?: WidgetQuerySchema; // Widget query configuration including filters
}

/**
 * Kanban widget for dashboards
 * Displays objects in a kanban board grouped by state
 *
 * Note: This widget doesn't use the time series data from the standard widget loader.
 * Instead, it fetches object-list data directly via the ObjectKanban component.
 */
export function KanbanWidget({ query }: KanbanWidgetProps) {
  const objectType = (query?.object_type as ObjectTypes) || 'deliverables';
  const filters = query?.filters || [];
  const timeRange = query?.time_range;
  const states = (query as any)?.states || undefined; // eslint-disable-line @typescript-eslint/no-explicit-any

  return (
    <div className="h-full w-full overflow-hidden">
      <ObjectKanban
        objectType={objectType}
        filters={filters}
        timeRange={timeRange}
        states={states}
      />
    </div>
  );
}
