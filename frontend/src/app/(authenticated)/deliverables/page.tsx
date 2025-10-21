'use client';

import { useState, useTransition, useCallback } from 'react';
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
import { ActionsMenu } from '@/components/actions-menu';
import { CreateDeliverableForm } from '@/components/actions/create-deliverable-form';
import type { ActionFormRenderer } from '@/hooks/use-action-executor';

export default function DeliverablesPage() {
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

  const { data } = useListObjectsSuspense('deliverables', request);

  // Store column definitions after first fetch
  if (data.columns && !columnDefs) {
    setColumnDefs(data.columns);
  }

  const handleBulkAction = (action: string, rows: typeof data.objects) => {
    console.log('Bulk action:', action, 'on rows:', rows);
    // TODO: Implement bulk action handling
  };

  const handleRowActionClick = (actionName: string, row: ObjectListDTO) => {
    console.log('Row action clicked:', actionName, 'on row:', row.id);
    // TODO: Implement row action handling with dynamic objectId
  };

  // Custom form renderer for deliverable actions
  const renderDeliverableActionForm: ActionFormRenderer = useCallback(
    (props) => {
      const { action, onSubmit, onCancel, isSubmitting } = props;

      // Handle create deliverable action with custom form
      if (
        action.action ===
        'top_level_deliverable_actions__top_level_deliverable_create'
      ) {
        return (
          <CreateDeliverableForm
            onSubmit={(deliverableData) => {
              // Pass to action executor
              onSubmit({
                action:
                  'top_level_deliverable_actions__top_level_deliverable_create',
                data: deliverableData,
              });
            }}
            onCancel={onCancel}
            isSubmitting={isSubmitting}
          />
        );
      }

      // Return null for actions that don't need custom forms
      return null;
    },
    []
  );

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
          placeholder="Search deliverables"
        />
        {data.actions && data.actions.length > 0 && (
          <ActionsMenu
            actions={data.actions}
            actionGroup="top_level_deliverable_actions"
            renderActionForm={renderDeliverableActionForm}
            onActionComplete={() => {
              // Refresh deliverables list after action completion
            }}
          />
        )}
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
