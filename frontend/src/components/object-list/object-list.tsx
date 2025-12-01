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
import type {
  ObjectListSchema,
  ObjectTypes,
  ActionDTO,
  ActionsActionGroupObjectIdExecuteObjectActionBody,
} from '@/openapi/ariveAPI.schemas';
import { useActionsActionGroupObjectIdExecuteObjectAction } from '@/openapi/actions/actions';
import { toast } from 'sonner';
import { useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { getErrorMessage } from '@/lib/error-handler';
import { getActionRenderer, type ActionType } from '@/lib/actions/registry';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import type { DomainObject } from '@/types/domain-objects';

interface ObjectListProps {
  objectType: ObjectTypes;
  pageSize?: number;
  enableSearch?: boolean;
  enableRowSelection?: boolean;
  enableSorting?: boolean;
  enableColumnVisibility?: boolean;
  enableColumnFilters?: boolean;
  searchPlaceholder?: string;
  onRowClick?: (row: ObjectListSchema) => void;
  onBulkAction?: (action: string, rows: ObjectListSchema[]) => void;
}

/**
 * ObjectList component - Handles all data table concerns including:
 * - Schema fetching (cached)
 * - State management (pagination, sorting, filtering, search)
 * - Data fetching via useListObjectsSuspense
 * - Rendering search, filters, and table
 *
 * Does NOT include PageTopBar - parent page should wrap this component.
 */
export function ObjectList({
  objectType,
  pageSize = 40,
  enableSearch = true,
  enableRowSelection = true,
  enableSorting = true,
  enableColumnVisibility = true,
  enableColumnFilters = true,
  searchPlaceholder,
  onRowClick,
  onBulkAction,
}: ObjectListProps) {
  // Table state
  const [paginationState, setPaginationState] = useState<PaginationState>({
    pageIndex: 0,
    pageSize,
  });
  const [sortingState, setSortingState] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [searchTerm, setSearchTerm] = useState<string | undefined>(undefined);
  const [isPending, startTransition] = useTransition();

  // Action execution state
  const [pendingAction, setPendingAction] = useState<{
    action: ActionDTO;
    rows: ObjectListSchema[];
  } | null>(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);

  // Query client and router for action handling
  const queryClient = useQueryClient();
  const router = useRouter();

  // Mutation for executing object actions
  const executeObjectActionMutation =
    useActionsActionGroupObjectIdExecuteObjectAction();

  // Fetch schema metadata (cacheable)
  const { data: schema } =
    useOObjectTypeSchemaGetObjectSchemaSuspense(objectType);

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

  const handleSearchChange = (value: string) => {
    startTransition(() => {
      setSearchTerm(value || undefined);
      setPaginationState((prev) => ({ ...prev, pageIndex: 0 }));
    });
  };

  // Build API request
  const { offset, limit } = paginationStateToRequest(paginationState);
  const request = {
    offset,
    limit,
    sorts: sortingStateToSortDefinitions(sortingState),
    filters: columnFiltersToRequestFilters(columnFilters, schema.columns),
    search: searchTerm && searchTerm.trim().length > 0 ? searchTerm : undefined,
  };

  // Fetch data
  const { data } = useListObjectsSuspense(objectType, request);

  // Execute action with API call
  const executeAction = async (
    action: ActionDTO,
    rows: ObjectListSchema[],
    actionData?: unknown
  ) => {
    setIsExecuting(true);

    try {
      // Determine if this is a bulk action or single row action
      const isBulk = rows.length > 1;
      const row = rows[0];

      // Build action body - the discriminated union requires the exact action string
      // We cast to the union type since we know action.action comes from the backend
      const actionBody = {
        action: action.action,
        data: actionData || {},
      } as ActionsActionGroupObjectIdExecuteObjectActionBody;

      let response;

      if (isBulk) {
        // For bulk actions, we need to execute the action for each row
        // TODO: Backend should support bulk operations natively
        const promises = rows.map((r) =>
          executeObjectActionMutation.mutateAsync({
            actionGroup: action.action_group_type,
            objectId: r.id,
            data: actionBody,
          })
        );
        const results = await Promise.all(promises);
        response = results[0]; // Use first response for success message
      } else {
        // Single row action
        response = await executeObjectActionMutation.mutateAsync({
          actionGroup: action.action_group_type,
          objectId: row.id,
          data: actionBody,
        });
      }

      // Show success toast
      toast.success(
        response.message || `${action.label} completed successfully`
      );

      // Handle query invalidation
      if (response.invalidate_queries) {
        response.invalidate_queries.forEach((queryKey) => {
          queryClient.invalidateQueries({ queryKey: [queryKey] });
        });
      }

      // Also invalidate the objects list
      queryClient.invalidateQueries({ queryKey: ['objects', objectType] });

      // Handle redirects
      if (response.action_result?.type === 'redirect') {
        router.push(response.action_result.path);
      }

      // Handle downloads
      if (response.action_result?.type === 'download_file') {
        window.open(response.action_result.url, '_blank');
      }

      // Close dialogs
      setShowConfirmation(false);
      setShowForm(false);
      setPendingAction(null);
    } catch (err) {
      const errorMessage = getErrorMessage(
        err,
        `Failed to execute ${action.label}`
      );
      toast.error(errorMessage);
    } finally {
      setIsExecuting(false);
    }
  };

  // Check if action has a custom form
  const hasCustomForm = (action: ActionDTO): boolean => {
    // Cast action.action to ActionType since it comes from the backend as a string
    const renderer = getActionRenderer(action.action as ActionType);
    if (!renderer) return false;

    // Check if renderer returns non-null
    return (
      renderer({
        objectData: undefined,
        onSubmit: () => {},
        onClose: () => {},
        isSubmitting: false,
        isOpen: false,
        actionLabel: action.label,
      }) !== null
    );
  };

  // Initiate an action (single or bulk)
  const initiateAction = (action: ActionDTO, rows: ObjectListSchema[]) => {
    setPendingAction({ action, rows });

    // If action has custom form, show form dialog
    if (hasCustomForm(action)) {
      setShowForm(true);
      return;
    }

    // If action has confirmation message, show confirmation dialog
    if (action.confirmation_message) {
      setShowConfirmation(true);
      return;
    }

    // Execute simple actions directly
    executeAction(action, rows);
  };

  // Row action handler
  const handleRowActionClick = (actionName: string, row: ObjectListSchema) => {
    // Find the action in the row's actions
    const action = row.actions?.find((a) => a.action === actionName);
    if (!action) {
      console.error('Action not found:', actionName);
      return;
    }

    initiateAction(action, [row]);

    // Also call the onRowClick callback if provided
    if (onRowClick) {
      onRowClick(row);
    }
  };

  // Bulk action handler
  const handleBulkAction = (actionName: string, rows: ObjectListSchema[]) => {
    if (rows.length === 0) return;

    // Find the action from the first row (all selected rows should have the same actions)
    const action = rows[0].actions?.find((a) => a.action === actionName);
    if (!action) {
      console.error('Action not found:', actionName);
      return;
    }

    initiateAction(action, rows);

    // Also call the onBulkAction callback if provided
    if (onBulkAction) {
      onBulkAction(actionName, rows);
    }
  };

  // Confirm and execute pending action
  const confirmAction = () => {
    if (pendingAction) {
      executeAction(pendingAction.action, pendingAction.rows);
    }
  };

  // Cancel pending action
  const cancelAction = () => {
    setShowConfirmation(false);
    setShowForm(false);
    setPendingAction(null);
  };

  // Execute action with form data
  const executeWithFormData = (data: unknown) => {
    if (pendingAction) {
      executeAction(pendingAction.action, pendingAction.rows, data);
    }
  };

  const placeholder = searchPlaceholder ?? `Search ${objectType}`;

  return (
    <div className="container mx-auto flex flex-col gap-2 p-6">
      {enableSearch && (
        <div className="flex items-center gap-4">
          <DataTableSearch
            value={searchTerm ?? ''}
            onChangeAction={handleSearchChange}
            placeholder={placeholder}
          />
        </div>
      )}
      {enableColumnFilters && (
        <DataTableAppliedFilters
          filters={columnFilters}
          columnDefs={schema.columns}
          onUpdate={handleFiltersChange}
        />
      )}
      <DataTable
        isLoading={isPending}
        columns={schema.columns}
        data={data.objects}
        totalCount={data.total}
        enableRowSelection={enableRowSelection}
        enableSorting={enableSorting}
        enableColumnVisibility={enableColumnVisibility}
        enableColumnFilters={enableColumnFilters}
        paginationState={paginationState}
        sortingState={sortingState}
        columnFilters={columnFilters}
        onPaginationChange={handlePaginationChange}
        onSortingChange={handleSortingChange}
        onFiltersChange={handleFiltersChange}
        onActionClick={handleRowActionClick}
        onBulkActionClick={handleBulkAction}
      />

      {/* Confirmation Dialog */}
      <AlertDialog open={showConfirmation} onOpenChange={setShowConfirmation}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              {pendingAction?.action.label || 'Confirm Action'}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {pendingAction?.action.confirmation_message ||
                'Are you sure you want to perform this action?'}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={cancelAction} disabled={isExecuting}>
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction onClick={confirmAction} disabled={isExecuting}>
              {isExecuting ? 'Processing...' : 'Continue'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Form Dialog */}
      {showForm &&
        pendingAction &&
        (() => {
          const renderer = getActionRenderer(
            pendingAction.action.action as ActionType
          );
          if (!renderer) return null;

          // Get object data from the first row (for single row actions)
          // ObjectListSchema has compatible shape with DomainObject for rendering purposes
          const objectData =
            pendingAction.rows.length === 1
              ? (pendingAction.rows[0] as unknown as DomainObject)
              : undefined;

          return renderer({
            objectData,
            onSubmit: executeWithFormData,
            onClose: cancelAction,
            isSubmitting: isExecuting,
            isOpen: showForm,
            actionLabel: pendingAction.action.label,
          });
        })()}
    </div>
  );
}
