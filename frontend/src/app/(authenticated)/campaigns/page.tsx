'use client';

import { useState, useTransition, useEffect, useMemo } from 'react';
import type {
  SortingState,
  ColumnFiltersState,
  PaginationState,
  Updater,
} from '@tanstack/react-table';
import { DataTable } from '@/components/data-table/data-table';
import { DataTableSearch } from '@/components/data-table/data-table-search';
import { DataTableAppliedFilters } from '@/components/data-table/data-table-applied-filters';
import { useListObjectsSuspense } from '@/openapi/objects/objects';
import {
  sortingStateToSortDefinitions,
  paginationStateToRequest,
  columnFiltersToRequestFilters,
} from '@/components/data-table/utils';
import type {
  ColumnDefinitionDTO,
  ObjectListDTO,
} from '@/openapi/managerLab.schemas';
import { ActionGroupType } from '@/openapi/managerLab.schemas';
import { useHeader } from '@/components/header-provider';
import type { ActionData } from '@/components/header-provider';
import { useQueryClient } from '@tanstack/react-query';

export default function CampaignsPage() {
  const queryClient = useQueryClient();
  const { setHeaderData } = useHeader();

  // Table state
  const [paginationState, setPaginationState] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 40,
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

  const { data } = useListObjectsSuspense('campaigns', request);

  // Store column definitions after first fetch
  if (data.columns && !columnDefs) {
    setColumnDefs(data.columns);
  }

  // Create actions data for the header
  const actionsData: ActionData | undefined = useMemo(() => {
    if (!data.actions) return undefined;

    return {
      actions: data.actions,
      actionGroup: ActionGroupType.top_level_campaign_actions,
      objectId: '', // No specific object for top-level actions
      onInvalidate: () => {
        queryClient.invalidateQueries({
          queryKey: ['/o/campaigns'],
        });
      },
    };
  }, [data.actions, queryClient]);

  // Set header data for top-level actions
  useEffect(() => {
    if (actionsData) {
      setHeaderData({
        title: 'Campaigns',
        actionsData,
      });
    }
    return () => {
      setHeaderData(null);
    };
  }, [actionsData, setHeaderData]);

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleBulkAction = (_action: string, _rows: typeof data.objects) => {
    // TODO: Implement bulk action handling
  };

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleRowActionClick = (_actionName: string, _row: ObjectListDTO) => {
    // TODO: Implement row action handling with dynamic objectId
  };

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
          placeholder="Search campaigns"
        />
      </div>
      {columnDefs && (
        <DataTableAppliedFilters
          filters={columnFilters}
          columnDefs={columnDefs}
          onUpdate={handleFiltersChange}
        />
      )}
      <DataTable
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
        onActionClick={handleRowActionClick}
        onBulkActionClick={handleBulkAction}
      />
    </div>
  );
}
