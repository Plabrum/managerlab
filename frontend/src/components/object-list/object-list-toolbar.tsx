import { configToColumnFilters } from './config-utils';
import { ObjectListFilterButton } from './object-list-filter-button';
import { ObjectListSortButton } from './object-list-sort-button';
import { SavedViewSettings } from './saved-view-settings';
import { DataTableAppliedFilters } from '@/components/data-table/data-table-applied-filters';
import { DataTableSearch } from '@/components/data-table/data-table-search';
import { columnFiltersToRequestFilters } from '@/components/data-table/utils';
import type {
  ColumnDefinitionSchema,
  ObjectListRequestFiltersItem,
  SortDefinition,
  SavedViewConfigSchema,
  SavedViewSchema,
  ObjectTypes,
} from '@/openapi/ariveAPI.schemas';
import type { ViewMode } from '@/types/view-modes';

interface ObjectListToolbarProps {
  // Object type and schema
  objectType: ObjectTypes;
  columns: ColumnDefinitionSchema[];

  // Current config state
  config: SavedViewConfigSchema;

  // Update callbacks (pure - no side effects)
  onSearchChange: (search: string) => void;
  onSortingChange: (sorting: SortDefinition[]) => void;
  onFiltersChange: (filters: ObjectListRequestFiltersItem[]) => void;
  onViewModeChange: (viewMode: ViewMode) => void;
  onColumnVisibilityChange: (visibility: Record<string, boolean>) => void;

  // SavedView props (optional)
  currentView?: SavedViewSchema;
  hasUnsavedChanges?: boolean;
  onViewSelect?: (id: unknown | null) => void;

  // Feature flags
  enableSearch?: boolean;
  enableFilters?: boolean;
  enableSorting?: boolean;
}

/**
 * Pure composition component that renders all toolbar controls.
 * No state, no effects - just composition and event forwarding.
 */
export function ObjectListToolbar({
  objectType,
  columns,
  config,
  onSearchChange,
  onSortingChange,
  onFiltersChange,
  onViewModeChange,
  onColumnVisibilityChange,
  currentView,
  hasUnsavedChanges = false,
  onViewSelect,
  enableSearch = true,
  enableFilters = true,
  enableSorting = true,
}: ObjectListToolbarProps) {
  // Convert config to typed formats for components
  const columnFilters = configToColumnFilters(config);
  const sorting = (config.sorting as unknown as SortDefinition[]) || [];
  const filters =
    (config.column_filters as unknown as ObjectListRequestFiltersItem[]) || [];

  return (
    <div className="flex flex-col gap-2">
      {/* Top row: Search + Controls */}
      <div className="flex items-center gap-2">
        {enableSearch && (
          <div className="flex-1">
            <DataTableSearch
              value={config.search_term ?? ''}
              onChangeAction={onSearchChange}
              placeholder={`Search ${objectType}`}
            />
          </div>
        )}

        {enableSorting && (
          <ObjectListSortButton
            columns={columns}
            sorting={sorting}
            onSortingChange={onSortingChange}
          />
        )}

        {enableFilters && (
          <ObjectListFilterButton
            columns={columns}
            filters={filters}
            onFiltersChange={onFiltersChange}
          />
        )}

        {currentView && (
          <div className="ml-auto">
            <SavedViewSettings
              objectType={objectType}
              currentView={currentView}
              viewMode={(config.display_mode as ViewMode) || 'table'}
              onViewModeChange={onViewModeChange}
              hasUnsavedChanges={hasUnsavedChanges}
              currentConfig={config}
              onViewSelect={onViewSelect}
              columns={columns}
              columnVisibility={config.column_visibility || {}}
              onColumnVisibilityChange={onColumnVisibilityChange}
            />
          </div>
        )}
      </div>

      {/* Second row: Applied filters */}
      {enableFilters && (
        <DataTableAppliedFilters
          filters={columnFilters}
          columnDefs={columns}
          onUpdate={(newFilters) => {
            // Convert TanStack column filters back to request format
            const requestFilters = columnFiltersToRequestFilters(
              newFilters,
              columns
            );
            onFiltersChange(requestFilters);
          }}
        />
      )}
    </div>
  );
}
