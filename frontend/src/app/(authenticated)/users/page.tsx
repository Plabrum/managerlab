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

export default function UsersPage() {
  // Table state
  const [paginationState, setPaginationState] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 40,
  });
  const [sortingState, setSortingState] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [searchTerm, setSearchTerm] = useState<string | undefined>(undefined);
  const [isPending, startTransition] = useTransition();

  // Fetch schema for column definitions
  const { data: schemaData } =
    useOObjectTypeSchemaGetObjectSchemaSuspense('users');
  const columnDefs = schemaData.columns;

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

  // Build API request inline
  const { offset, limit } = paginationStateToRequest(paginationState);
  const request = {
    offset,
    limit,
    sorts: sortingStateToSortDefinitions(sortingState),
    filters: columnDefs
      ? columnFiltersToRequestFilters(columnFilters, columnDefs)
      : [],
    search: searchTerm && searchTerm.trim().length > 0 ? searchTerm : undefined,
  };

  const { data } = useListObjectsSuspense('users', request);

  // TODO: Implement bulk action handling

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <DataTableSearch
          value={searchTerm ?? ''}
          onChangeAction={(value) => {
            startTransition(() => {
              setSearchTerm(value || undefined);
              setPaginationState((prev) => ({ ...prev, pageIndex: 0 }));
            });
          }}
          placeholder="Search users"
        />
        {/* TODO: Add ActionsMenu when user_actions ActionGroupType is added to backend */}
      </div>
      <DataTableAppliedFilters
        filters={columnFilters}
        columnDefs={columnDefs}
        onUpdate={handleFiltersChange}
      />
      <DataTable
        isLoading={isPending}
        columns={columnDefs}
        data={data.objects}
        totalCount={data.total}
        enableRowSelection={true}
        enableSorting={true}
        enableColumnVisibility={true}
        enableColumnFilters={true}
        paginationState={paginationState}
        sortingState={sortingState}
        columnFilters={columnFilters}
        onPaginationChange={handlePaginationChange}
        onSortingChange={handleSortingChange}
        onFiltersChange={handleFiltersChange}
      />
    </div>
  );
}
