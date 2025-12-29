/**
 * Utilities for converting between SavedViewConfigSchema and UI state formats.
 * These are pure functions with no side effects.
 */

import type {
  SortingState,
  ColumnFiltersState,
  PaginationState,
} from '@tanstack/react-table';
import {
  columnFiltersToRequestFilters,
  requestFiltersToColumnFilters,
} from '@/components/data-table/utils';
import { SortDirection } from '@/openapi/ariveAPI.schemas';
import type {
  SavedViewConfigSchema,
  SortDefinition,
  ObjectListRequestFiltersItem,
  ColumnDefinitionSchema,
} from '@/openapi/ariveAPI.schemas';

/**
 * Get default config for a new view
 */
export function getDefaultConfig(): SavedViewConfigSchema {
  return {
    display_mode: 'table',
    column_filters: [],
    column_visibility: {},
    sorting: [],
    search_term: null,
    page_size: 40,
    schema_version: 1,
  };
}

/**
 * Convert SavedViewConfigSchema to TanStack Table's SortingState
 */
export function configToSortingState(
  config: SavedViewConfigSchema
): SortingState {
  if (!config.sorting || config.sorting.length === 0) {
    return [];
  }

  // Now properly typed in SavedViewConfigSchema
  return config.sorting.map((sort) => ({
    id: sort.column,
    desc: sort.direction === SortDirection.sort_desc,
  }));
}

/**
 * Convert TanStack Table's SortingState to SortDefinition[] format
 */
export function sortingStateToConfig(
  sortingState: SortingState
): SortDefinition[] {
  return sortingState.map((sort) => ({
    column: sort.id,
    direction: sort.desc ? SortDirection.sort_desc : SortDirection.sort_asc,
  }));
}

/**
 * Convert SavedViewConfigSchema to TanStack Table's ColumnFiltersState
 */
export function configToColumnFilters(
  config: SavedViewConfigSchema
): ColumnFiltersState {
  if (!config.column_filters || config.column_filters.length === 0) {
    return [];
  }

  // Now properly typed in SavedViewConfigSchema
  return requestFiltersToColumnFilters(config.column_filters);
}

/**
 * Convert TanStack Table's ColumnFiltersState to SavedViewConfigSchema format
 */
export function columnFiltersToConfig(
  columnFilters: ColumnFiltersState,
  columns: ColumnDefinitionSchema[]
): ObjectListRequestFiltersItem[] {
  return columnFiltersToRequestFilters(columnFilters, columns);
}

/**
 * Convert SavedViewConfigSchema to PaginationState
 * Note: pageIndex is NOT stored in config (it's transient UI state)
 */
export function configToPaginationState(
  config: SavedViewConfigSchema,
  pageIndex: number
): PaginationState {
  return {
    pageIndex,
    pageSize: config.page_size || 40, // Default to 40 if not set
  };
}

/**
 * Create a config updater function that preserves schema_version
 */
export function createConfigUpdater(
  setConfig: React.Dispatch<React.SetStateAction<SavedViewConfigSchema>>
) {
  return (updates: Partial<SavedViewConfigSchema>) => {
    setConfig((prev) => ({
      ...prev,
      ...updates,
      schema_version: prev.schema_version, // Always preserve version
    }));
  };
}

/**
 * Deep equality check for config objects (for change detection)
 */
export function configsAreEqual(
  a: SavedViewConfigSchema | undefined,
  b: SavedViewConfigSchema | undefined
): boolean {
  if (!a || !b) return a === b;

  // Compare display mode
  if (a.display_mode !== b.display_mode) return false;

  // Compare search term (normalize null/undefined/empty)
  const aSearch = a.search_term || null;
  const bSearch = b.search_term || null;
  if (aSearch !== bSearch) return false;

  // Compare page size
  if (a.page_size !== b.page_size) return false;

  // Compare sorting
  if (JSON.stringify(a.sorting) !== JSON.stringify(b.sorting)) return false;

  // Compare filters
  if (JSON.stringify(a.column_filters) !== JSON.stringify(b.column_filters))
    return false;

  // Compare column visibility
  const aVisKeys = Object.keys(a.column_visibility || {});
  const bVisKeys = Object.keys(b.column_visibility || {});
  if (aVisKeys.length !== bVisKeys.length) return false;
  for (const key of aVisKeys) {
    if (a.column_visibility?.[key] !== b.column_visibility?.[key]) return false;
  }

  return true;
}

/**
 * Get a display label for current sorting state
 */
export function getSortingLabel(
  config: SavedViewConfigSchema,
  columns: ColumnDefinitionSchema[]
): string {
  if (!config.sorting || config.sorting.length === 0) {
    return 'None';
  }

  // Now properly typed in SavedViewConfigSchema
  const sort = config.sorting[0];
  const column = columns.find((col) => col.key === sort.column);
  if (!column) return 'None';

  const direction = sort.direction === SortDirection.sort_asc ? 'A-Z' : 'Z-A';
  return `${column.label} (${direction})`;
}
