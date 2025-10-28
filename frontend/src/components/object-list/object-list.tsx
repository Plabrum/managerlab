'use client';

import { useState, useTransition } from 'react';
import type {
  SortingState,
  ColumnFiltersState,
  PaginationState,
  Updater,
} from '@tanstack/react-table';
import { DataTable } from '@/components/data-table/data-table';
import { DataTableSearch } from '@/components/data-table/data-table-search';
import { DataTableAppliedFilters } from '@/components/data-table/data-table-applied-filters';
import {
  useListObjectsSuspense,
  useOObjectTypeSchemaGetObjectSchemaSuspense,
} from '@/openapi/objects/objects';
import {
  sortingStateToSortDefinitions,
  paginationStateToRequest,
  columnFiltersToRequestFilters,
} from '@/components/data-table/utils';
import type { ObjectListDTO, ObjectTypes } from '@/openapi/managerLab.schemas';

interface ObjectListProps {
  objectType: ObjectTypes;
  pageSize?: number;
  enableSearch?: boolean;
  enableRowSelection?: boolean;
  enableSorting?: boolean;
  enableColumnVisibility?: boolean;
  enableColumnFilters?: boolean;
  searchPlaceholder?: string;
  onRowClick?: (row: ObjectListDTO) => void;
  onBulkAction?: (action: string, rows: ObjectListDTO[]) => void;
}

/**
 * ObjectList component - Handles all data table concerns including:
 * - Schema fetching (cached)
 * - State management (pagination, sorting, filtering, search)
 * - Data fetching via useListObjectsSuspense
 * - Rendering search, filters, and table
 *
 * Does NOT include PageTopBar - parent page should wrap this component.
 */
export function ObjectList({
  objectType,
  pageSize = 40,
  enableSearch = true,
  enableRowSelection = true,
  enableSorting = true,
  enableColumnVisibility = true,
  enableColumnFilters = true,
  searchPlaceholder,
  onRowClick,
  onBulkAction,
}: ObjectListProps) {
  // Table state
  const [paginationState, setPaginationState] = useState<PaginationState>({
    pageIndex: 0,
    pageSize,
  });
  const [sortingState, setSortingState] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [searchTerm, setSearchTerm] = useState<string | undefined>(undefined);
  const [isPending, startTransition] = useTransition();

  // Fetch schema metadata (cacheable)
  const { data: schema } =
    useOObjectTypeSchemaGetObjectSchemaSuspense(objectType);

  // Wrap state updates in startTransition to prevent Suspense fallback
  const handlePaginationChange = (updater: Updater<PaginationState>) => {
    startTransition(() => setPaginationState(updater));
  };

  const handleSortingChange = (updater: Updater<SortingState>) => {
    startTransition(() => setSortingState(updater));
  };

  const handleFiltersChange = (updater: Updater<ColumnFiltersState>) => {
    startTransition(() => setColumnFilters(updater));
  };

  const handleSearchChange = (value: string) => {
    startTransition(() => {
      setSearchTerm(value || undefined);
      setPaginationState((prev) => ({ ...prev, pageIndex: 0 }));
    });
  };

  // Build API request
  const { offset, limit } = paginationStateToRequest(paginationState);
  const request = {
    offset,
    limit,
    sorts: sortingStateToSortDefinitions(sortingState),
    filters: columnFiltersToRequestFilters(columnFilters, schema.columns),
    search: searchTerm && searchTerm.trim().length > 0 ? searchTerm : undefined,
  };

  // Fetch data
  const { data } = useListObjectsSuspense(objectType, request);

  // Default row action handler (no-op for now)
  const handleRowActionClick = (_actionName: string, _row: ObjectListDTO) => {
    // TODO: Implement row action handling with dynamic objectId
    if (onRowClick) {
      onRowClick(_row);
    }
  };

  // Default bulk action handler
  const handleBulkAction = (action: string, rows: ObjectListDTO[]) => {
    if (onBulkAction) {
      onBulkAction(action, rows);
    }
  };

  const placeholder = searchPlaceholder ?? `Search ${objectType}`;

  return (
    <>
      {enableSearch && (
        <div className="flex items-center gap-4">
          <DataTableSearch
            value={searchTerm ?? ''}
            onChangeAction={handleSearchChange}
            placeholder={placeholder}
          />
        </div>
      )}
      {enableColumnFilters && (
        <DataTableAppliedFilters
          filters={columnFilters}
          columnDefs={schema.columns}
          onUpdate={handleFiltersChange}
        />
      )}
      <DataTable
        isLoading={isPending}
        columns={schema.columns}
        data={data.objects}
        totalCount={data.total}
        enableRowSelection={enableRowSelection}
        enableSorting={enableSorting}
        enableColumnVisibility={enableColumnVisibility}
        enableColumnFilters={enableColumnFilters}
        paginationState={paginationState}
        sortingState={sortingState}
        columnFilters={columnFilters}
        onPaginationChange={handlePaginationChange}
        onSortingChange={handleSortingChange}
        onFiltersChange={handleFiltersChange}
        onActionClick={handleRowActionClick}
        onBulkActionClick={handleBulkAction}
      />
    </>
  );
}
