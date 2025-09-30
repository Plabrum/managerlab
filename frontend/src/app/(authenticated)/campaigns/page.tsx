'use client';

import { useState } from 'react';
import type {
  SortingState,
  ColumnFiltersState,
  PaginationState,
  Updater,
} from '@tanstack/react-table';
import { NewDataTable } from '@/components/data-table/new-data-table';
import { useListObjectsSuspense } from '@/openapi/objects/objects';
import { createObjectListRequest } from '@/components/data-table/utils';

export default function CampaignsPage() {
  // Table state
  const [paginationState, setPaginationState] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });
  const [sortingState, setSortingState] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

  // Create wrapper functions for React Table callbacks
  const handlePaginationChange = (updaterOrValue: Updater<PaginationState>) => {
    if (typeof updaterOrValue === 'function') {
      setPaginationState((prev) => updaterOrValue(prev));
    } else {
      setPaginationState(updaterOrValue);
    }
  };

  const handleSortingChange = (updaterOrValue: Updater<SortingState>) => {
    if (typeof updaterOrValue === 'function') {
      setSortingState((prev) => updaterOrValue(prev));
    } else {
      setSortingState(updaterOrValue);
    }
  };

  const handleFiltersChange = (updaterOrValue: Updater<ColumnFiltersState>) => {
    if (typeof updaterOrValue === 'function') {
      setColumnFilters((prev) => updaterOrValue(prev));
    } else {
      setColumnFilters(updaterOrValue);
    }
  };

  // Create API request from table state
  const request = createObjectListRequest(
    'campaigns',
    paginationState,
    sortingState,
    columnFilters
  );

  // Fetch data using Orval suspense query
  const { data } = useListObjectsSuspense('campaigns', request);

  return (
    <div className="container mx-auto py-6">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Campaigns</h1>
          <p className="text-muted-foreground">
            Manage and view all your campaigns.
          </p>
        </div>

        <NewDataTable
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
        />
      </div>
    </div>
  );
}
