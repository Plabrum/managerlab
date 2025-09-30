'use client';

import { useState, useTransition } from 'react';
import type {
  SortingState,
  ColumnFiltersState,
  PaginationState,
  Updater,
} from '@tanstack/react-table';
import { NewDataTable } from '@/components/data-table/new-data-table';
import { DataTableSearch } from '@/components/data-table/data-table-search';
import { DataTableAppliedFilters } from '@/components/data-table/data-table-applied-filters';
import { useListObjectsSuspense } from '@/openapi/objects/objects';
import {
  sortingStateToSortDefinitions,
  paginationStateToRequest,
  columnFiltersToRequestFilters,
} from '@/components/data-table/utils';
import type { ColumnDefinitionDTO } from '@/openapi/managerLab.schemas';

export default function RosterPage() {
  // Table state
  const [paginationState, setPaginationState] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });
  const [sortingState, setSortingState] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [searchTerm, setSearchTerm] = useState<string | undefined>(undefined);
  const [columnDefs, setColumnDefs] = useState<
    ColumnDefinitionDTO[] | undefined
  >(undefined);
  const [isPending, startTransition] = useTransition();

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

  // Store column definitions after first fetch
  if (data.columns && !columnDefs) {
    setColumnDefs(data.columns);
  }

  const handleBulkAction = (action: string, rows: typeof data.objects) => {
    console.log('Bulk action:', action, 'on rows:', rows);
    // TODO: Implement bulk action handling
  };

  return (
    <div className="space-y-4">
      <DataTableSearch
        value={searchTerm ?? ''}
        onChangeAction={(value) => {
          startTransition(() => {
            setSearchTerm(value || undefined);
            setPaginationState((prev) => ({ ...prev, pageIndex: 0 }));
          });
        }}
        placeholder="Search roster"
      />
      {columnDefs && (
        <DataTableAppliedFilters
          filters={columnFilters}
          columnDefs={columnDefs}
          onUpdate={handleFiltersChange}
        />
      )}
      <NewDataTable
        isLoading={isPending}
        columns={data.columns}
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
        onBulkActionClick={handleBulkAction}
      />
    </div>
  );
}
