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
import { ActionGroupType } from '@/openapi/managerLab.schemas';
import { useQueryClient } from '@tanstack/react-query';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectActions } from '@/components/object-detail';

export default function DeliverablesPage() {
  const queryClient = useQueryClient();

  // Table state
  const [paginationState, setPaginationState] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 40,
  });
  const [sortingState, setSortingState] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [searchTerm, setSearchTerm] = useState<string | undefined>(undefined);
  const [isPending, startTransition] = useTransition();

  // Fetch schema metadata (cacheable)
  const { data: schema } =
    useOObjectTypeSchemaGetObjectSchemaSuspense('deliverables');

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
    filters: columnFiltersToRequestFilters(columnFilters, schema.columns),
    search: searchTerm && searchTerm.trim().length > 0 ? searchTerm : undefined,
  };

  // Fetch data (without schema metadata)
  const { data } = useListObjectsSuspense('deliverables', request);

  // Invalidation callback for top-level actions
  const handleInvalidate = () => {
    queryClient.invalidateQueries({
      queryKey: ['/o/deliverables'],
    });
  };

  // TODO: Implement row action handling (see media page for reference)
  // TODO: Implement bulk action handling

  return (
    <PageTopBar
      title="Deliverables"
      actions={
        <ObjectActions
          actions={data.actions}
          actionGroup={ActionGroupType.top_level_deliverable_actions}
          onInvalidate={handleInvalidate}
        />
      }
    >
      <div className="flex items-center gap-4">
        <DataTableSearch
          value={searchTerm ?? ''}
          onChangeAction={(value) => {
            startTransition(() => {
              setSearchTerm(value || undefined);
              setPaginationState((prev) => ({ ...prev, pageIndex: 0 }));
            });
          }}
          placeholder="Search deliverables"
        />
      </div>
      <DataTableAppliedFilters
        filters={columnFilters}
        columnDefs={schema.columns}
        onUpdate={handleFiltersChange}
      />
      <DataTable
        isLoading={isPending}
        columns={schema.columns}
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
    </PageTopBar>
  );
}
