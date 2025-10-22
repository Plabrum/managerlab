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
import { useActionExecutor } from '@/hooks/use-action-executor';
import { ActionConfirmationDialog } from '@/components/actions/action-confirmation-dialog';
import { ActionFormDialog } from '@/components/actions/action-form-dialog';

export default function MediaPage() {
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
  const [selectedObjectId, setSelectedObjectId] = useState<string | undefined>(
    undefined
  );

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

  const { data } = useListObjectsSuspense('media', request);

  // Store column definitions after first fetch
  if (data.columns && !columnDefs) {
    setColumnDefs(data.columns);
  }

  // Action executor for row-level actions
  const rowActionExecutor = useActionExecutor({
    actionGroup: 'media_actions',
    objectId: selectedObjectId,
  });

  const handleBulkAction = (action: string, rows: typeof data.objects) => {
    console.log('Bulk action:', action, 'on rows:', rows);
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
          placeholder="Search media"
        />
        {data.actions && data.actions.length > 0 && (
          <ActionsMenu
            actions={data.actions}
            actionGroup="top_level_media_actions"
            onActionComplete={() => {
              // Refresh the media list after action completion
              // Note: For media upload, the refresh happens via the register mutation
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
    </div>
  );
}
