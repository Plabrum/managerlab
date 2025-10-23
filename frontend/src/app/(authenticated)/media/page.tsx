'use client';

import {
  useState,
  useTransition,
  useCallback,
  useEffect,
  useMemo,
} from 'react';
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
import { useActionExecutor } from '@/hooks/use-action-executor';
import { ActionConfirmationDialog } from '@/components/actions/action-confirmation-dialog';
import { ActionFormDialog } from '@/components/actions/action-form-dialog';

export default function MediaPage() {
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

  // Create actions data for the header
  const actionsData: ActionData | undefined = useMemo(() => {
    if (!data.actions) return undefined;

    return {
      actions: data.actions,
      actionGroup: ActionGroupType.top_level_media_actions,
      objectId: '',
      onInvalidate: () => {
        queryClient.invalidateQueries({
          predicate: (query) =>
            query.queryKey[0] === 'listObjects' &&
            query.queryKey[1] === 'media',
        });
      },
    };
  }, [data.actions, queryClient]);

  // Set header data for top-level actions
  useEffect(() => {
    if (actionsData) {
      setHeaderData({
        title: 'Media',
        actionsData,
      });
    }
    return () => {
      setHeaderData(null);
    };
  }, [actionsData, setHeaderData]);

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
