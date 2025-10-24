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
import type { ObjectListDTO } from '@/openapi/managerLab.schemas';
import { ActionGroupType } from '@/openapi/managerLab.schemas';
import { useQueryClient } from '@tanstack/react-query';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectActions } from '@/components/object-detail';

export default function InvoicesPage() {
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
    useOObjectTypeSchemaGetObjectSchemaSuspense('invoices');

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
  const { data } = useListObjectsSuspense('invoices', request);

  // Invalidation callback for top-level actions
  const handleInvalidate = () => {
    queryClient.invalidateQueries({
      queryKey: ['/o/invoices'],
    });
  };

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleBulkAction = (_action: string, _rows: typeof data.objects) => {
    // TODO: Implement bulk action handling
  };

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleRowActionClick = (_actionName: string, _row: ObjectListDTO) => {
    // TODO: Implement row action handling with dynamic objectId
  };

  return (
    <PageTopBar
      title="Invoices"
      actions={
        <ObjectActions
          actions={data.actions}
          actionGroup={ActionGroupType.top_level_invoice_actions}
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
          placeholder="Search invoices"
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
        onActionClick={handleRowActionClick}
        onBulkActionClick={handleBulkAction}
      />
    </PageTopBar>
  );
}
