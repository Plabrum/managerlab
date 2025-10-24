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
import { useActionExecutor } from '@/hooks/use-action-executor';
import { ActionConfirmationDialog } from '@/components/actions/action-confirmation-dialog';
import { ActionFormDialog } from '@/components/actions/action-form-dialog';

export default function MediaPage() {
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
  const [selectedObjectId, setSelectedObjectId] = useState<string | undefined>(
    undefined
  );

  // Fetch schema metadata (cacheable)
  const { data: schema } = useOObjectTypeSchemaGetObjectSchemaSuspense('media');

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
  const { data } = useListObjectsSuspense('media', request);

  // Invalidation callback for top-level actions
  const handleInvalidate = () => {
    queryClient.invalidateQueries({
      queryKey: ['/o/media'],
    });
  };

  // Action executor for row-level actions
  const rowActionExecutor = useActionExecutor({
    actionGroup: 'media_actions',
    objectId: selectedObjectId,
  });

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleBulkAction = (_action: string, _rows: typeof data.objects) => {
    // TODO: Implement bulk action handling
  };

  const handleRowActionClick = useCallback(
    (actionName: string, row: ObjectListDTO) => {
      // Set the selected object ID
      setSelectedObjectId(row.id);

      // Find the action from the row's actions
      const action = row.actions?.find((a) => a.action === actionName);
      if (action) {
        // Use the row action executor to initiate the action
        rowActionExecutor.initiateAction(action);
      }
    },
    [rowActionExecutor]
  );

  return (
    <PageTopBar
      title="Media"
      actions={
        <ObjectActions
          actions={data.actions}
          actionGroup={ActionGroupType.top_level_media_actions}
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
          placeholder="Search media"
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

      {/* Row action dialogs */}
      <ActionConfirmationDialog
        open={rowActionExecutor.showConfirmation}
        action={rowActionExecutor.pendingAction}
        isExecuting={rowActionExecutor.isExecuting}
        onConfirm={rowActionExecutor.confirmAction}
        onCancel={rowActionExecutor.cancelAction}
      />

      {rowActionExecutor.showForm &&
        rowActionExecutor.pendingAction &&
        rowActionExecutor.renderActionForm && (
          <ActionFormDialog
            open={rowActionExecutor.showForm}
            action={rowActionExecutor.pendingAction}
            isExecuting={rowActionExecutor.isExecuting}
            onCancel={rowActionExecutor.cancelAction}
          >
            {rowActionExecutor.renderActionForm({
              action: rowActionExecutor.pendingAction,
              onSubmit: rowActionExecutor.executeWithData,
              onCancel: rowActionExecutor.cancelAction,
              isSubmitting: rowActionExecutor.isExecuting,
            })}
          </ActionFormDialog>
        )}
    </PageTopBar>
  );
}
